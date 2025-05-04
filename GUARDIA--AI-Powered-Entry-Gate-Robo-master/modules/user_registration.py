# modules/user_registration.py

import cv2
import face_recognition
from modules.utils import add_user

def register_user(name, mobile, face_encoding):
    if face_encoding is not None:
        add_user(name, mobile, face_encoding)
        print(f"User {name} registered successfully.")
        return True
    else:
        print("Face encoding not available.")
        return False

