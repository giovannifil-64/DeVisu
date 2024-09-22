"""
* cameraUtils.py
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

import cv2
import time
import os

class PathStorage:
    def __init__(self):
        self._path = ""

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path

class VideoCamera:
    def __init__(self):
        self.camera = None
        self.camera_status = "Not Initialized"
        self.face_detected_time = None
        self.captured_image_path = PathStorage()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if self.face_cascade.empty():
            print("Error loading face cascade classifier.")
            self.camera_status = "Error"

    def initialize_camera(self):
        if self.camera is not None:
            self.release_camera()
        
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("Failed to open the camera.")
            self.camera_status = "Error"
        else:
            print(f"Camera opened successfully. Backend: {self.camera.getBackendName()}")
            print(f"Frame width: {self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)}")
            print(f"Frame height: {self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            print(f"FPS: {self.camera.get(cv2.CAP_PROP_FPS)}")
            self.camera_status = "Success"

    def release_camera(self):
        if self.camera is not None and self.camera.isOpened():
            self.camera.release()
            self.camera = None
            self.camera_status = "Released"
            print("Camera released")

    def __del__(self):
        self.release_camera()

    def get_frame(self):
        if self.camera is None or not self.camera.isOpened():
            self.initialize_camera()
        
        if self.camera_status == "Error" or not self.camera.isOpened():
            print("Camera is not available or opened.")
            return None

        max_retries = 5
        for _ in range(max_retries):
            success, frame = self.camera.read()
            if success:
                break
            print("Failed to read frame from camera. Retrying...")
            time.sleep(0.5)
        
        if not success:
            print("Failed to read frame after multiple attempts.")
            return None

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.15, minNeighbors=5, minSize=(30, 30))
                        
        if len(faces) == 1:
            if self.face_detected_time is None:
                self.face_detected_time = time.time()
            elif time.time() - self.face_detected_time >= 2:
                self.capture_image(frame, faces[0])
                self.face_detected_time = None
                print(f"CAPTURE_IMAGE FROM FUNCTION: {self.captured_image_path.path}")
                return "captured"
        else:
            self.face_detected_time = None

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        ret, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()

    def capture_image(self, frame, face_coords):
        self.captured_image_path.path = ""

        (x, y, w, h) = face_coords
        padding = 20
        x1 = max(x - padding, 0)
        y1 = max(y - padding, 0)
        x2 = min(x + w + padding, frame.shape[1])
        y2 = min(y + h + padding, frame.shape[0])

        face_img = frame[y1:y2, x1:x2]

        img_filename = "captured_image{}.jpg".format(time.strftime("%Y%m%d-%H%M%S"))
        cv2.imwrite(img_filename, face_img)
        path = os.path.abspath(img_filename)

        if os.path.exists(path):
            print(f"Image successfully saved as {path}")
        else:
            print(f"Failed to save image as {path}")

        # Assign the path to the path storage
        self.captured_image_path.path = path
        print(f"CAPTURE_IMAGE FROM CLASS: {self.captured_image_path.path}")
        return path
    
    def ensure_camera_is_open(self):
        if not self.camera.isOpened():
            print("Attempting to reopen the camera...")
            self.camera.release()
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("Failed to reopen the camera.")
                self.camera_status = "Error"
            else:
                print("Camera reopened successfully.")
                self.camera_status = "Success"

    def get_captured_path(self):
        print(f"Retrieving captured path: {self.captured_image_path.path}")
        return self.captured_image_path.path

    def set_captured_path(self, new_path):
        self.captured_image_path.path = new_path


