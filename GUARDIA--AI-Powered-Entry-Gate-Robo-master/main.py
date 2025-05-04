# main.py

import cv2
import time
import threading
from modules.assistant import GuardiaAssistant
from modules.mode_switching import ModeSwitching
from modules.user_registration import register_user
from modules.face_recognition_module import FaceRecognitionModule
from modules.text_to_speech_module import TextToSpeechModule, AzureTextToSpeechModule
from modules.speech_recognition_module import SpeechRecognitionModule, AzureSpeechRecognitionModule
from modules.utils import init_database, generate_random_access_key, add_user_entry_log, get_user_entry_log

def main():
    init_database()
    face_recognition_module = FaceRecognitionModule()
    speech_recognition_module = SpeechRecognitionModule()
    azure_speech_recognition_module = AzureSpeechRecognitionModule()
    azure_text_to_speech_module = AzureTextToSpeechModule()
    text_to_speech_module = TextToSpeechModule()
    mode_switching = ModeSwitching()
    assistant = GuardiaAssistant()

    cap = None
    listening = False

    def video_stream():
        nonlocal cap, listening
        while True:
            if mode_switching.current_mode == 'security':
                cap = cv2.VideoCapture(0)
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    face_data = face_recognition_module.detect_and_recognize(frame)
                    if face_data is None or len(face_data) == 0:
                        continue
                    else:
                        for face in face_data:
                            if face['name'] == 'unknown':
                                if face['encoding'] is None:
                                    continue
                                listening = True
                                handle_unknown_user(face['encoding'])
                                listening = False
                            else:
                                if not face['id']:
                                    continue
                                handle_recognized_faces(face)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                cap.release()
                cv2.destroyAllWindows()
            else:
                if cap is not None:
                    cap.release()
                cv2.destroyAllWindows()

    def handle_unknown_user(face_encoding):
        azure_text_to_speech_module.speak("You are not recognized. Please provide your name")
        while True:
            name, mobile = get_user_input()
            azure_text_to_speech_module.speak(f"Thank you {name}. I have recorded your mobile number as {mobile}. Is that correct?")
            response = azure_speech_recognition_module.listen(cmd=True)
            if 'yes' in response or 'ya' in response or 'yeah' in response or 'correct' in response or 'haan' in response:
                if register_user(name, mobile, face_encoding):
                    accesskey = generate_random_access_key()
                    azure_text_to_speech_module.speak(f"Hey {name}, your access key is {accesskey}")
                    add_user_entry_log(name, accesskey)
                    break
                else:
                    azure_text_to_speech_module.speak("User registration failed, please try again")
            else:
                azure_text_to_speech_module.speak("Please provide your name again")
        return name

    def handle_recognized_faces(data):
        log = get_user_entry_log(data['id'])
        if log:
            print(f"Welcome {data['name']}")
        else:
            accesskey = generate_random_access_key()
            add_user_entry_log(data['name'], accesskey, data['image'])
            azure_text_to_speech_module.speak(f"Hey {data['name']}, your access key is {accesskey}")

    def get_user_input():
        name = azure_speech_recognition_module.listen()
        azure_text_to_speech_module.speak("Please provide your mobile number")
        mobile = azure_speech_recognition_module.listen()
        return name, mobile

    def audio_processing():
        nonlocal listening
        while True:
            if listening:
                continue
            command = speech_recognition_module.listen(cmd=True)
            if 'assistant mode' in command:
                switch_to_assistant_mode()
            elif 'security mode' in command:
                mode_switching.switch_mode('security')
                text_to_speech_module.speak("Switched to security mode")
            elif mode_switching.current_mode == 'assistant':
                response = assistant.process_assistant_commands(command)
                text_to_speech_module.speak(response)

    def switch_to_assistant_mode():
        text_to_speech_module.speak("Please provide the password to switch to assistant mode")
        password = speech_recognition_module.listen(cmd=True)
        if password == 'password':
            mode_switching.switch_mode('assistant')
            text_to_speech_module.speak("Switched to assistant mode")
        else:
            text_to_speech_module.speak("Incorrect password")


    # video_thread = threading.Thread(target=video_stream)
    # audio_thread = threading.Thread(target=audio_processing)

    try:
        # video_thread.start()
        # audio_thread.start()
        video_stream()
        # video_thread.join()
        # audio_thread.join()
    except KeyboardInterrupt:
        print("Terminating program...")
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
