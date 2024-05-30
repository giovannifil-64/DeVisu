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
    image = cv2.imread(image_path)
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) == 0:
        return None
    else:
        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        face_image_resized = cv2.resize(face_image, (512, 512))
        face_vector = face_recognition.face_encodings(image)

        if len(face_vector) == 0:
            return None
        else:
            return face_vector[0]

# def compare_face_vectors(vector1, vector2, threshold=0.5): #0.6
#     # Calculate Euclidean distance between the vectors
#     euclidean_distance = np.linalg.norm(vector1 - vector2)
    
#     # Check if the distance is within the threshold
#     if euclidean_distance <= threshold:
#         return True
#     else:
#         return False
    
def compare_vectors(vector1, vector2, threshold=0.6):
    """Compare two vectors using cosine similarity."""
    scalar_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    similarity = scalar_product / (norm_vector1 * norm_vector2)
    
    return similarity >= threshold
    
def base64_encoder(vector):
    # Convert the face vector to bytes
    face_vector_bytes = vector.tobytes()
    # Encode the byte representation as base64
    face_vector_base64 = base64.b64encode(face_vector_bytes).decode('utf-8')
    return face_vector_base64

def base64_decoder(base64_string):
    # Decode base64 string to bytes
    decoded_bytes = base64.b64decode(base64_string)
    # Convert bytes to numpy array to get the original vector
    vector = np.frombuffer(decoded_bytes, dtype=np.float64)
    return vector

"""if __name__ == "__main__":
    # Test the functions
    image1 = "static/img/img_2.jpg"
    image2 = "static/img/img_3.jpg"
    
    vector1 = get_face_vector(image1)
    vector2 = get_face_vector(image2)
    
    if vector1 is not None and vector2 is not None:
        print("Face vectors extracted successfully")
        print("Vector 1:", vector1)
        print("Vector 2:", vector2)
        
        base64_string1 = base64_encoder(vector1)
        base64_string2 = base64_encoder(vector2)
        
        print("Base64 String 1:", base64_string1)
        print("Base64 String 2:", base64_string2)
        
        vector1_decoded = base64_decoder(base64_string1)
        vector2_decoded = base64_decoder(base64_string2)
        
        print("Decoded Vector 1:", vector1_decoded)
        print("Decoded Vector 2:", vector2_decoded)
        
        result = compare_face_vectors(vector1, vector2)
        print("Face vectors match:", result)
    else:
        print("No face detected in one or both images")"""