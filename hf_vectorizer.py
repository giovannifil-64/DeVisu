"""
* hf_vectorizer.py
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

import base64
import cv2
import face_recognition
import numpy as np

def get_face_vector(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to read image from path: {image_path}")
            return None

        face_locations = face_recognition.face_locations(image)
        if len(face_locations) == 0:
            print("No faces detected in the image.")
            return None

        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        face_image_resized = cv2.resize(face_image, (512, 512))
        face_vector = face_recognition.face_encodings(face_image_resized)

        if len(face_vector) == 0:
            print("Failed to generate face vector from the detected face.")
            return None

        return face_vector[0]

    except Exception as e:
        print(f"Error occurred during face vector generation: {e}")
        return None

def compare_vectors(db_vector, camera_vector, tolerance=0.5):
    if db_vector is None or len(db_vector) == 0 or camera_vector is None:
        return False
    
    arracy_vct1 = np.atleast_2d(db_vector)
    arracy_vct2 = np.atleast_2d(camera_vector)
    
    distances = np.linalg.norm(arracy_vct1 - arracy_vct2, axis=1)
    
    return np.any(distances <= tolerance)

    
def base64_encoder(vector):
    face_vector_bytes = vector.tobytes()
    face_vector_base64 = base64.b64encode(face_vector_bytes).decode("utf-8")
    return face_vector_base64

def base64_decoder(base64_string):
    decoded_bytes = base64.b64decode(base64_string)
    vector = np.frombuffer(decoded_bytes, dtype=np.float64)
    return vector