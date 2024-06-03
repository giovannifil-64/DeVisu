/*
 * camera.js
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
 */

window.addEventListener('unload', function () {
    fetch('/release_camera')
        .then(response => {
            if (response.ok) {
                console.log('Camera released successfully');
            } else {
                console.error('Failed to release camera');
            }
        })
        .catch(error => {
            console.error('Error releasing camera:', error);
        });
});

function checkCaptureStatus(redirectUrl) {
    fetch('/check_capture_status')
        .then(response => response.text())
        .then(status => {
            if (status === 'captured') {
                // Redirect to the specified URL if the capture status is 'captured'
                window.location.href = redirectUrl;
            }
        })
        .catch(error => {
            console.error('Error checking capture status:', error);
        });
}

function startCheckingCaptureStatus(redirectUrl) {
    setInterval(() => checkCaptureStatus(redirectUrl), 500);
}
