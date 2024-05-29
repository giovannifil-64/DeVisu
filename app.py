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
import cv2
import hf_vectorizer
import os
import requests

from camera import VideoCamera
from database import setup_database
from flask import render_template, Response, request, redirect, url_for, jsonify
from hf_vectorizer import base64_encoder, base64_decoder, compare_vectors
from users import read_all, create, read_one, update, delete
from utils import generate_otp

BASE_URL = 'http://localhost:5000/api/users'

app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml")

flask_app = app.app
flask_app.config['DEBUG'] = True

camera = None
capture_status = {"status": "not_captured"}

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

"""
Directory structure:

DeVisu
├── templates/
│   ├── home.html (Main page)

│   ├── add_name.html (Ask for the name of the person to add)
│   ├── add_person.html (capture the image of the person)
│   ├── face_check.html (generate the face vector and OTP and store it in the database)
│   └── add_result.html (display the result of the face vectorization)
│
│   ├── verify_otp.html (Ask for the OTP of the person to verify)
│   ├── verify_capture.html (Capture the image of the person to verify)
│   ├── verify_check.html (Compare the face vector with the one on the database corresponding to the OTP)
│   └── verify_result.html (Display the result of the face comparison)
│
│   ├── remove_person.html (Ask for the OTP to remove the person from the database, and check if the person exists given the OTP)
│   ├── remove_capture.html (Capture the image of the person to remove)
│   └── remove_result.html (Display the result of the removal)

"""

# main page
@app.route("/")
def home():
    camera_status = initialize_camera()
    if camera_status.startswith("Error"):
        print(f"(app.index)Error: {camera_status}")
        return camera_status
    return render_template("home.html")

### Add a new person to the database ###

# Step 1: Ask for the name of the person to add
@app.route('/add_name', methods=['GET'])
def add_name_get():
    return render_template('add_name.html', step=1)

# Handle the form submission
@app.route('/add_name', methods=['POST'])
def add_name_post():    
    username = request.form['username']
    print(f"(app.submit)Name: {username}")
    set_global_name(username)
    return redirect(url_for("add_person"))

# Step 2: Capture the image of the person
@app.route('/add_person')
def add_person():
    camera_status = initialize_camera()
    if camera_status.startswith("Error"):
        return camera_status
    return render_template('add_person.html', step=2, username=g_name)

# Step 3: Generate the face vector and OTP and store it in the database.
@app.route('/add_vectorization')
def add_vectorization():
    global g_otp, g_vector
    
    release_camera()
    if VideoCamera.g_img_path is None:
        return "Image path is not available. Please capture an image first."

    img_path = VideoCamera.g_img_path
    img = cv2.imread(img_path)
    if img is None:
        return f"Failed to read image at path: {img_path}"

    str_img_path = str(img_path)
    set_global_vector(hf_vectorizer.get_face_vector(str_img_path))
    set_global_otp(generate_otp())
    
    os.remove(str_img_path)
    
    return render_template('add_vectorization.html', step=3)

# Step 4: Show the result and the OTP to the user.
@app.route('/add_result')
def add_result():
    global g_name, g_otp, g_vector
    
    release_camera()
    
    new_user = {
        "id": 0, # Placeholder value, will be ignored by the API
        'name': g_name,
        'otp': str(g_otp),
        'vector': base64_encoder(g_vector)
    }

    response = requests.post(BASE_URL, json=new_user)

    if response.status_code == 201:
        print('User created successfully!')
        created_user = response.json()
        print(f'User ID: {created_user["id"]}')
    else:
        print(f'Error creating user: {response.text}')
        
    temp_name, temp_otp = g_name, g_otp
    
    reset_globals()
    print(f"Globals reset: {g_name}, {g_otp}, {g_vector}, {g_obtained_vector}")
    # print(f"video_path BEFORE={VideoCamera.g_img_path}")
    # VideoCamera.set_global_path("")
    # print(f"video_path AFTER={VideoCamera.g_img_path}")    
    return render_template('add_result.html', step=4, username=temp_name, otp=temp_otp)

### Verify a person in the database ###

# Step 1: Ask for the OTP of the person to verify
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'GET':
        return render_template('verify_otp.html')
    else:
        otp = request.form['otp']
        user = get_user_by_otp(otp)

        if user:
            # print(f"User vector: {user['vector']}")
            set_global_obtained_vector(base64_decoder(user['vector']))
            return render_template('verify_capture.html', user=user)
        else:
            error = f"User with OTP {otp} not found"
            return render_template('verify_result.html', error=error)
        
# Step 2: Capture the image of the person to verify
@app.route('/verify_capture')
def verify_capture():
    camera_status = initialize_camera()
    if camera_status.startswith("Error"):
        return camera_status
    print(f"Camera status: {camera_status}")
    return render_template('verify_capture.html')

# Step 3: Compare the face vector with the one on the database corresponding to the OTP
@app.route('/verify_check')
def verify_check():
    global g_obtained_vector, g_vector
    release_camera()
    if VideoCamera.g_img_path is None:
        return render_template('verify_result.html', error="Image path is not available. Please capture an image first.")

    img_path = VideoCamera.g_img_path
    img = cv2.imread(img_path)
    print(f"Image path: {img_path}")
    if img is None:
        print(f"app.verify_check: Failed to read image at path: {img_path}")
        return render_template('verify_result.html', error=f"Failed to read image at path: {img_path}")

    str_img_path = str(img_path)
    set_global_vector(hf_vectorizer.get_face_vector(str_img_path))

    if compare_vectors(g_obtained_vector, g_vector):
        print("Verification successful!")
        result = "Verification successful!"
    else:
        print("Verification failed.")
        result = "Verification failed."
        
    
    os.remove(str_img_path)

    return render_template('verify_result.html', result=result)

### Remove a person from the database ###

# Step 1: Ask for the OTP to remove the person from the database, and check if the person exists given the OTP

# Step 2: Capture the image of the person to remove



# Utils
@app.route('/video_feed')
def video_feed():
    initialize_camera()
    return Response(generate(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_capture_status')
def check_capture_status():
    return capture_status["status"]

@app.route('/release_camera')
def release_camera_route():
    release_camera()  # Call the function to release the camera
    return 'Camera released'

@app.route('/users/by_otp/<string:otp>', methods=['GET'])
def get_user_by_otp(otp):
    user = get_user_by_otp(otp)
    if user:
        return user
    else:
        return jsonify({'error': 'User not found'}), 404

def initialize_camera():
    global camera
    if camera is None:
        camera = VideoCamera()
        if camera.camera_status == "Error":
            return "(app.initialize_camera)Error: Failed to open the camera."
    return "(app.initialize_camera)Camera initialized successfully."

def release_camera():
    global camera
    if camera is not None:
        camera.__del__()
        camera = None

def generate(camera):
    while True:
        try:
            frame = camera.get_frame()
            if frame == "captured":
                capture_status["status"] = "captured"
                break
            if frame is None:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except Exception as e:
            print(f"Error generating frame: {e}")
            break
        
def get_user_by_otp(otp):
    url = f"{BASE_URL}/by_otp/{otp}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return None  # User not found
    else:
        return None  # Other errors, handle appropriately if needed

# Initialize the database
setup_database()

# Define the routes
app.add_url_rule('/users', 'read_all', read_all, methods=['GET'])
app.add_url_rule('/users', 'create', create, methods=['POST'])
app.add_url_rule('/users/<int:userId>', 'read_one', read_one, methods=['GET'])
app.add_url_rule('/users/<int:userId>', 'update', update, methods=['PUT'])
app.add_url_rule('/users/<int:userId>', 'delete', delete, methods=['DELETE'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
### STOP CODE BEFORE REFACTorig ###