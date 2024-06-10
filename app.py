"""
* app.py
* 
* Copyright 2024, Filippini Giovanni
* 
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*         https://www.apache.org/licenses/LICENSE-2.0.txt
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
"""

import connexion
import hf_vectorizer
import os
import requests

from cameraUtils import *
from database import setup_database
from flask import render_template, Response, request, redirect, url_for, jsonify
from hf_vectorizer import base64_encoder, base64_decoder, compare_vectors
from users import read_all, create, read_one, update, delete
from toolbox import generate_otp

BASE_URL = "http://localhost:5000/api/users"

app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml")

flask_app = app.app
flask_app.config["DEBUG"] = True

camera = None
capture_status = {"status": "not_captured"}
captured_image_path = PathStorage()

g_name = ""
g_otp = ""
g_vector = ""
g_obtained_vector = ""

def set_global_name(name):
    global g_name
    g_name = name
    
def set_global_otp(otp):
    global g_otp
    g_otp = otp
    
def set_global_vector(vector):
    global g_vector
    g_vector = vector
    
def set_global_obtained_vector(vector):
    global g_obtained_vector
    g_obtained_vector = vector
    
def reset_globals():
    global g_name, g_otp, g_vector, g_obtained_vector
    set_global_name("")
    set_global_otp("")
    set_global_vector("")
    set_global_obtained_vector("")

# Main page
@app.route("/")
def home():
    is_empty = is_database_empty()
    return render_template("home.html", is_database_empty=is_empty)

### Add a new person to the database ###

# Step 1: Ask for the name of the person to add
@app.route("/add_name", methods=["GET"])
def add_name_get():
    return render_template("add_name.html", step=1)

# Handle the form submission
@app.route("/add_name", methods=["POST"])
def add_name_post():    
    username = request.form["username"]
    print(f"(app.submit)Name: {username}")
    set_global_name(username)
    return redirect(url_for("add_person"))

# Step 2: Capture the image of the person
@app.route("/add_person")
def add_person():
    camera_status = initialize_camera()
    if camera_status.startswith("Error"):
        return camera_status

    while True:
        frame_status = camera.get_frame()
        if frame_status == "captured":
            break

    return render_template("add_person.html", step=2, username=g_name)

# Step 3: Generate the face vector and OTP and store it in the database.
@app.route("/add_vectorization")
def add_vectorization():
    global g_otp, g_vector

    camera_status = initialize_camera()
    if camera_status.startswith("Error"):
        return camera_status

    img_path = camera.get_captured_path()
    if img_path is None or img_path == "":
        return "Image path is not available. Please capture an image first."

    str_img_path = str(img_path)
    vectorizer = hf_vectorizer.get_face_vector(str_img_path)
    if vectorizer is None:
        return "Failed to generate face vector from the captured image."
    
    set_global_vector(vectorizer)
    set_global_otp(generate_otp())
    print(f"Generated OTP: {g_otp}")

    delete_all_images()
    return render_template("add_vectorization.html", step=3)

# Step 4: Show the result and the OTP to the user.
@app.route("/add_result")
def add_result():
    global g_name, g_otp, g_vector

    new_user = {
        "id": 0, # Placeholder value, will be ignored by the API
        "name": g_name,
        "otp": str(g_otp),
        "vector": base64_encoder(g_vector)
    }

    response = requests.post(BASE_URL, json=new_user)

    if response.status_code == 201:
        created_user = response.json()
        result = "Person added correctly!"
        tmp_user, tmp_otp = g_name, g_otp

        release_camera()
        reset_globals()
        return render_template("result.html", step=4, operation="add", result=result, username=tmp_user, otp=tmp_otp)
    else:
        print(f"Error creating user: {response.text}")
        error = "Error creating user"
        release_camera()
        reset_globals()
        return render_template("result.html", step=4, operation="add", result=result, username=tmp_user, otp=tmp_otp)

### Verify a person in the database ###

# Step 1: Ask for the OTP of the person to verify
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "GET":
        return render_template("verify_otp.html", step=1)
    else:
        otp = request.form["otp"]
        user = get_user_by_otp(otp)

        if user:
            set_global_obtained_vector(base64_decoder(user["vector"]))
            return render_template("verify_capture.html", user=user, step=1)
        else:
            error = f"User with OTP {otp} not found. Please try again."
            return render_template("result.html", error=error, step=3)
        
# Step 2: Capture the image of the person to verify
@app.route("/verify_capture")
def verify_capture():
    camera_status = initialize_camera()
    
    if camera_status.startswith("Error"):
        return camera_status

    while True:
        frame_status = camera.get_frame()
        if frame_status == "captured":
            break
    return render_template("verify_capture.html", step=2)

# Step 3: Compare the face vector with the one on the database corresponding to the OTP
@app.route("/verify_check")
def verify_check():
    global g_obtained_vector

    # Capture the image first
    camera_status = initialize_camera()
    if camera_status.startswith("Error"):
        return camera_status

    while True:
        frame_status = camera.get_frame()
        if frame_status == "captured":
            break

    if g_obtained_vector is None:
        release_camera()
        return render_template("result.html", error="No face detected during verification.", step=3, operation="verify")

    img_path = camera.get_captured_path()
    if img_path is None or img_path == "":
        release_camera()
        return render_template("result.html", error="Image path is not available. Please capture an image first.", step=3, operation="verify")

    str_img_path = str(img_path)
    generated_vector = hf_vectorizer.get_face_vector(str_img_path)

    if generated_vector is None:
        release_camera()
        return render_template("result.html", error="Failed to generate face vector from the captured image.", step=3, operation="verify")

    if not compare_vectors(g_obtained_vector, generated_vector):
        print("Verification failed.")
        result = "Verification failed."
        release_camera()
        return render_template("result.html", result=result, step=3, operation="verify")

    result = "Verification successful!"

    release_camera()
    delete_all_images()
    return render_template("result.html", result=result, step=3, operation="verify")


### Remove a person from the database ###

# Step 1: Ask for the OTP of the person to delete
@app.route("/delete_otp", methods=["GET", "POST"])
def delete_otp():
    if request.method == "GET":
        return render_template("delete_otp.html", step=1)
    else:
        otp = request.form["otp"]
        user = get_user_by_otp(otp)

        if user:
            set_global_obtained_vector(base64_decoder(user["vector"]))
            set_global_otp(otp)
            return render_template("delete_capture.html", user=user, step=1)
        else:
            error = f"The person with OTP {otp} not found. Please try again."
            return render_template("delete_result.html", error=error, step=3)

# Step 2: Capture the image of the person to delete
@app.route("/delete_capture")
def delete_capture():
    camera_status = initialize_camera()
    
    if camera_status.startswith("Error"):
        return camera_status

    while True:
        frame_status = camera.get_frame()
        if frame_status == "captured":
            break
    return render_template("delete_capture.html", step=2)

# Step 3: Compare the face vector and delete the user if vectors match
@app.route("/delete_check")
def delete_check():
    global g_obtained_vector, g_otp

    # Initialize the camera first
    camera_status = initialize_camera()
    if camera_status.startswith("Error"):
        return camera_status

    while True:
        frame_status = camera.get_frame()
        if frame_status == "captured":
            break

    if g_obtained_vector is None:
        release_camera()
        return render_template("result.html", error="No face detected during deletion.", step=3)

    img_path = camera.get_captured_path()
    if img_path is None or img_path == "":
        release_camera()
        return render_template("result.html", error="Image path is not available. Please capture an image first.", step=3, operation="delete")

    generated_vector = hf_vectorizer.get_face_vector(str(img_path))

    if generated_vector is None:
        release_camera()
        return render_template("result.html", error="Failed to generate face vector from the captured image.", step=3, operation="delete")

    if not compare_vectors(g_obtained_vector, generated_vector):
        print("Deletion failed.")
        result = "Deletion failed."
        release_camera()
        return render_template("result.html", result=result, step=3, operation="delete")

    delete_user_by_otp(g_otp)
    result = "Deletion successful!"

    delete_all_images()
    release_camera()
    return render_template("result.html", result=result, step=3, operation="delete")


# utils routes
@app.route("/video_feed")
def video_feed():
    camera_status = initialize_camera()
    if camera_status.startswith("Error"):
        return camera_status

    return Response(generate(camera), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/check_capture_status")
def check_capture_status():
    return capture_status["status"]

@app.route("/release_camera")
def release_camera_route():
    release_camera()
    return "Camera released"

@app.route("/users/by_otp/<string:otp>", methods=["GET"])
def get_user_by_otp(otp):
    user = get_user_by_otp(otp)
    
    if user:
        return user
    else:
        return jsonify({"error": "User not found"}), 404
    
# @app.route('/open_external_link/<path:url>')
# def open_external_link(url):
#     return redirect(f'https://{url}', code=302)

# Utils functions
def release_camera():
    global camera
    
    if camera is not None:
        camera.camera.release()
        del camera
    camera = None

def initialize_camera():
    global camera
    
    if camera is None:
        camera = VideoCamera()
        if camera.camera_status == "Error":
            return "(app.initialize_camera)Error: Failed to open the camera."
    else:
        print("Camera is already initialized.")
    return "(app.initialize_camera)Camera initialized successfully."

def generate(camera):
    while True:
        try:
            frame = camera.get_frame()
            if frame is None:
                print("Error: Failed to read frame from camera.")
                continue
            elif frame == "captured":
                capture_status["status"] = "captured"
                break
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")
        except Exception as e:
            print(f"Error generating frame: {e}")
            break

def delete_all_images():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(script_dir)
    for file in os.listdir(script_dir):
        if file.endswith(".jpg"):
            file_path = os.path.join(script_dir, file)
            print(f"Deleted file: {file} at path: {file_path}")
            os.remove(file_path)
            
def get_user_by_otp(otp):
    url = f"{BASE_URL}/by_otp/{otp}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return None
    else:
        return None
    
def delete_user_by_otp(otp):
    url = f"{BASE_URL}/by_otp/{otp}"
    response = requests.get(url)

    if response.status_code == 200:
        user = response.json()
        user_id = user["id"]
        delete_url = f"{BASE_URL}/{user_id}"
        delete_response = requests.delete(delete_url)

        if delete_response.status_code == 200:
            print(f"User with OTP {otp} deleted successfully.")
        else:
            print(f"Failed to delete user with OTP {otp}. Error: {delete_response.text}")
    else:
        print(f"User with OTP {otp} not found.")

def is_database_empty():
    users = read_all()
    print(f"Total users: {len(users)}")
    return len(users) == 0

# Initialize the database
setup_database()

# Define API routes
app.add_url_rule("/users", "read_all", read_all, methods=["GET"])
app.add_url_rule("/users", "create", create, methods=["POST"])
app.add_url_rule("/users/<int:userId>", "read_one", read_one, methods=["GET"])
app.add_url_rule("/users/<int:userId>", "update", update, methods=["PUT"])
app.add_url_rule("/users/<int:userId>", "delete", delete, methods=["DELETE"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
