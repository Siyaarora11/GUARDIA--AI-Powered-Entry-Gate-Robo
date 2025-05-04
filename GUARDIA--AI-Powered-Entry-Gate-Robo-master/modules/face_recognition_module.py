# modules/face_recognition_module.py

import os
import cv2
import face_recognition
from modules.utils import get_known_faces
from config import HAAR_CASCADE_MODEL, FACE_DISTANCE

class FaceRecognitionModule:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_MODEL)
        self.known_face_names, self.known_face_encodings, self.known_face_ids = get_known_faces()

    def detect_and_recognize(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        face_names = []

        self.re_fetch()

        for (x, y, w, h) in faces:
            # Calculate the distance of the face from the camera
            distance = self.calculate_distance(w)
            print(f"Distance: {distance:.2f} meters")
            if distance > FACE_DISTANCE:
                continue  # Skip faces that are more than {FACE_DISTANCE} meter away
            rgb_face = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_face)
            face_encodings = face_recognition.face_encodings(rgb_face, face_locations)

            image = self.capture_image_bytes(frame)
            data = {
                "name": 'unknown',
                "id": None,
                "image": image,
                "encoding": None
            }
            if face_encodings:
                data["encoding"] = face_encodings[0]
                if self.known_face_encodings:  # Check if known faces exist
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encodings[0])
                    print(f"Matches: {matches}")
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encodings[0])
                    best_match_index = face_distances.argmin()
                    if matches[best_match_index]:
                        data["name"] = self.known_face_names[best_match_index]
                        data["id"] = self.known_face_ids[best_match_index]
                else:
                    print("No known faces to compare with.")
            else:
                print("Face encoding could not be generated.")
                continue
            face_names.append(data)
        return face_names

    def capture_image_bytes(self, frame):
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            return None
        # Convert the buffer to bytes
        image_bytes = buffer.tobytes()
        return image_bytes

    def calculate_distance(self, face_width):
        # Assuming a known face width (in meters) and focal length (in pixels)
        KNOWN_FACE_WIDTH = 0.15  # Average face width in meters
        FOCAL_LENGTH = 600  # Example focal length in pixels

        # Calculate the distance from the camera to the face
        distance = (KNOWN_FACE_WIDTH * FOCAL_LENGTH) / face_width
        return distance

    def re_fetch(self):
        self.known_face_names, self.known_face_encodings, self.known_face_ids = get_known_faces()