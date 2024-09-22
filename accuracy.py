"""
* accuracy.py
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

# The sccuracy is calculated by comparing the face vectors of the test images with the reference vectors of known persons.
# The dataset used for testing contains 2400 images of 80 persons (30 images per person).
# The dataset can be downloaded from GitHub: https://github.com/oscardelgado02/Face-Dataset---2400-IMG-and-80-LABELS

import os
from hf_vectorizer import get_face_vector, compare_vectors

def generate_reference_vectors(image_folder):
    reference_vectors = {}
    for person in range(1, 81):  # Persons 1 to 80
        image_path = os.path.join(image_folder, f"{person}_1.png")
        if os.path.exists(image_path):
            vector = get_face_vector(image_path)
            if vector is not None:
                reference_vectors[person] = vector
            else:
                print(f"Failed to generate vector for person {person}")
        else:
            print(f"Reference image for person {person} not found")
    return reference_vectors

def test_accuracy(image_folder, reference_vectors):
    results = {'TP': 0, 'FP': 0, 'TN': 0, 'FN': 0}
    processed_images = 0
    failed_images = 0

    for filename in os.listdir(image_folder):
        person_id = int(filename.split('_')[0])
        if f"{person_id}_1" in filename:
            continue
        
        test_vector = get_face_vector(os.path.join(image_folder, filename))
        if test_vector is None:
            print(f"Failed to generate vector for {filename}")
            failed_images += 1
            continue
        
        processed_images += 1
        
        correct_match = False
        for ref_person, ref_vector in reference_vectors.items():
            is_match = compare_vectors(ref_vector, test_vector, tolerance=0.5)
            
            if person_id == ref_person:
                if is_match:
                    results['TP'] += 1
                    correct_match = True
                    break
            elif is_match:
                results['FP'] += 1
                correct_match = True
                break
        
        if not correct_match:
            if person_id in reference_vectors:
                results['FN'] += 1
            else:
                results['TN'] += 1

    print(f"Processed {processed_images} images successfully.")
    print(f"Failed to process {failed_images} images.")
    
    return results

def calculate_accuracy(results):
    total = sum(results.values())
    accuracy = (results['TP'] + results['TN']) / total if total > 0 else 0
    
    print("Overall Results:")
    print(f"True Positives: {results['TP']}")
    print(f"True Negatives: {results['TN']}")
    print(f"False Positives: {results['FP']}")
    print(f"False Negatives: {results['FN']}")
    print(f"Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    image_folder = "/Users/giovannifilippini/Desktop/Face-Dataset---2400-IMG-and-80-LABELS-main/DATA"
    
    print("Generating reference vectors...")
    reference_vectors = generate_reference_vectors(image_folder)
    
    print("Testing accuracy...")
    results = test_accuracy(image_folder, reference_vectors)
    
    calculate_accuracy(results)

"""
0.45
True Positives: 513
True Negatives: 114
False Positives: 1
False Negatives: 595
Accuracy: 51.27%

0.50
True Positives: 803
True Negatives: 113
False Positives: 4
False Negatives: 303
Accuracy: 74.90%

0.55
True Positives: 945
True Negatives: 98
False Positives: 52
False Negatives: 128
Accuracy: 85.28%

0.60
True Positives: 837
True Negatives: 59
False Positives: 302
False Negatives: 25
Accuracy: 73.26%
"""