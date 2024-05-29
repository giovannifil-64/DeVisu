import cv2
import time 
import os 
 
class VideoCamera:
    g_img_path = ""  # Define as a class attribute
     
    def __init__(self):
        self.camera = cv2.VideoCapture(0) # Use the default camera. On macOS 1 is for the continuity camera
        if not self.camera.isOpened():
            print("(VideoCamera.__init__)Error: Failed to open the camera.")
            self.camera_status = "Error"
        else: 
            print("(VideoCamera.__init__)Camera opened successfully.")
            self.camera_status = "Success"
            """self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)  # Set width
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)  # Set height"""
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.face_detected_time = None  # Initialize the time of face detection
 
    def __del__(self):
        self.camera.release()
 
    @classmethod
    def set_global_path(cls, entry):
        cls.g_img_path = entry
 
    def get_frame(self):
        if self.camera_status == "Error": 
            return None
 
        success, frame = self.camera.read() 
        if not success:
            return None
 
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.15, minNeighbors=6, minSize=(30, 30))
        
        if len(faces) > 0: 
            if self.face_detected_time is None: 
                self.face_detected_time = time.time()  # Record the time when the face is first detected 
            elif time.time() - self.face_detected_time >= 2:  # Check if 2 seconds have passed 
                self.capture_image(frame, faces[0])  # Pass the coordinates of the first detected face 
                self.face_detected_time = None  # Reset the time after capturing the image 
                return "captured" 
        else: 
            self.face_detected_time = None  # Reset the time if no face is detected 
 
        for (x, y, w, h) in faces: 
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2) 
 
        ret, jpeg = cv2.imencode('.jpg', frame) 
        return jpeg.tobytes() 
 
    def capture_image(self, frame, face_coords): 
        (x, y, w, h) = face_coords 
        padding = 20 
        x1 = max(x - padding, 25) 
        y1 = max(y - padding, 10) 
        x2 = min(x + w + padding, frame.shape[1]) 
        y2 = min(y + h + padding, frame.shape[0]) 

        face_img = frame[y1:y2, x1:x2] 

        img_filename = "captured_image{}.jpg".format(time.strftime("%Y%m%d-%H%M%S")) 
        cv2.imwrite(img_filename, face_img) 
        # Obtain full path of the captured image 
        path = os.path.abspath(img_filename)
        
        # Set the global image path directly
        VideoCamera.g_img_path = path
        print(f"Image captured and saved as {VideoCamera.g_img_path}")
