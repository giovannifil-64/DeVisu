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
    """Encapsulated path storage."""
    def __init__(self):
        self._path = ""

    @property
    def path(self):
        """Get the stored path."""
        return self._path

    @path.setter
    def path(self, new_path):
        """Set the stored path."""
        self._path = new_path

class VideoCamera:
    """Class to handle video camera operations."""
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.captured_image_path = PathStorage()  # Encapsulated path storage
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        if not self.camera.isOpened():
            print("Failed to open the camera.")
            exit(1)
        else:
            print("Camera opened successfully.")
            self.camera_status = "Success"
            self.face_detected_time = None

    def __del__(self):
        self.camera.release()

    def get_frame(self):
        """Get a frame from the camera feed."""
        if self.camera_status == "Error":
            return None

        success, frame = self.camera.read()
        if not success:
            print("Failed to read frame from camera.")
            exit(2)
            # return None

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.15, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 1:
            # time.sleep(2)  # Wait for 2 seconds before capturing the image
            # self.capture_image(frame, faces[0])
            # print(f"CAPTURE_IMAGE FROM FUNCTION: {self.captured_image_path.path}")
            # return "captured"
            if self.face_detected_time is None:
                self.face_detected_time = time.time()
            elif time.time() - self.face_detected_time >= 3:
                self.capture_image(frame, faces[0])
                self.face_detected_time = None
                print(f"CAPTURE_IMAGE FROM FUNCTION: {self.captured_image_path.path}")
                return "captured"
        elif len(faces) > 1 or len(faces) == 0:
            self.face_detected_time = None
        else:
            print("No face detected.")
            self.face_detected_time = None  # Reset the time if no face is detected

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def capture_image(self, frame, face_coords):
        """Capture and save an image when a face is detected."""
        # Reset the path storage
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
    
    def get_captured_path(self):
        """Get the path of the captured image."""
        return self.captured_image_path.path
    
    def set_captured_path(self, new_path):
        """Set the path of the captured image."""
        self.captured_image_path.path = new_path
