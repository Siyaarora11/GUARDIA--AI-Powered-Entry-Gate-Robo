# modules/speech_recognition_module.py

import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk
from modules.text_to_speech_module import AzureTextToSpeechModule
from config import SPEECH_KEY, SPEECH_REGION, SPEECH_LANG

class SpeechRecognitionModule:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen(self, cmd=False):
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        try:
            print("Recognizing...")
            command = self.recognizer.recognize_google(audio)
            print(f"Recognized: {command}")
            if cmd:
                return command.lower()
            return command
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""


class AzureSpeechRecognitionModule:
    def __init__(self):
        self.text_to_speech = AzureTextToSpeechModule()
        self.speechsdk = speechsdk
        self.speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        self.speech_config.speech_recognition_language = SPEECH_LANG
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)
    
    def recognize_from_microphone(self):
        """
        Recognizes speech from the microphone and returns the recognized text.
    
        Returns:
            str: The recognized text or an empty string if no speech was recognized or if recognition was canceled.
        """    
        try:
            while True:
                speech_recognition_result = self.speech_recognizer.recognize_once_async().get()

                if speech_recognition_result.reason == self.speechsdk.ResultReason.RecognizedSpeech:
                    print(f"Recognized: {speech_recognition_result.text}")
                    return speech_recognition_result.text
                elif speech_recognition_result.reason == self.speechsdk.ResultReason.NoMatch:
                    print(f"No speech could be recognized: {speech_recognition_result.no_match_details}")
                    self.text_to_speech.speak("I'm sorry, I didn't catch that. Could you please repeat?")
                elif speech_recognition_result.reason == self.speechsdk.ResultReason.Canceled:
                    cancellation_details = speech_recognition_result.cancellation_details
                    print(f"Speech Recognition canceled: {cancellation_details.reason}")
                    if cancellation_details.reason == self.speechsdk.CancellationReason.Error:
                        print(f"Error details: {cancellation_details.error_details}")
                        print("Did you set the speech resource key and region values?")
                    return ""
                # If no valid speech is recognized, continue the loop
        except Exception as e:
            print(f"An error occurred during speech recognition: {e}")
            return ""

    def listen(self, cmd=False):
        result = self.recognize_from_microphone()
        if cmd:
            result = result.strip().strip('.,!?')
            return result.lower()
        return result