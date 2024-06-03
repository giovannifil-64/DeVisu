"""
* playground.py
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

import requests

# Base URL for the API
BASE_URL = 'http://localhost:5000/api/users'

"""# Create a new user
new_user = {
    "id": 0, # Placeholder value, will be ignored by the API
    'name': 'John Doe',
    'otp': '123456',
    'vector': 'some_vector_data'
}

response = requests.post(BASE_URL, json=new_user)

if response.status_code == 201:
    print('User created successfully!')
    created_user = response.json()
    print(f'User ID: {created_user["id"]}')
else:
    print(f'Error creating user: {response.text}')
"""

def delete_user_by_otp(otp):
    url = f"{BASE_URL}/by_otp/{otp}"
    response = requests.get(url)

    if response.status_code == 200:
        user = response.json()
        user_id = user['id']
        delete_url = f"{BASE_URL}/{user_id}"
        print(f"URL: {delete_url}")
        delete_response = requests.delete(delete_url)

        if delete_response.status_code == 200:
            print(f"User with OTP {otp} deleted successfully.")
        else:
            print(f"Failed to delete user with OTP {otp}. Error: {delete_response.text}")
    else:
        print(f"User with OTP {otp} not found.")

if __name__ == '__main__':
    delete_user_by_otp('314057')