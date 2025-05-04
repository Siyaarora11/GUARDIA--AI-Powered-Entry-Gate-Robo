import os
import random
import datetime
from openai import OpenAI
from config import API_KEY
from modules.text_to_speech_module import TextToSpeechModule
from modules.speech_recognition_module import SpeechRecognitionModule

class GuardiaAssistant:
    def __init__(self):
        self.system = ["You are Guardia, a helpful assistant."]
        self.user = []
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY,
        )

    def chat(self, query, max_tokens=100):
        self.user.append(query)
        try:
            completion = self.client.chat.completions.create(
                model="liquid/lfm-40b:free",
                messages=[
                    {"role": "system", "content": msg} for msg in self.system
                ] + [
                    {"role": "user", "content": msg} for msg in self.user
                ],
                max_tokens=max_tokens,
                top_p=0.9,
            )
            response = completion.choices[0].message.content
            self.system.append(response)
            return response
        except Exception as e:
            return str('An error occurred: ')

    def process_assistant_commands(self, command):
        trigger_phrases = ['hey guardia', 'ok guardia', 'ok guardian', 'hey guardian']
        for phrase in trigger_phrases:
            if command.startswith(phrase):
                command = command.replace(phrase, '').strip()
                if 'time' in command:
                    return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
                if command == '':
                    return "I'm sorry, I didn't catch that"
                else:
                    return self.chat(command)


def assistant():
    assis = GuardiaAssistant()
    speech_recognition_module = SpeechRecognitionModule()
    text_to_speech_module = TextToSpeechModule()

    text_to_speech_module.speak("How can I help you?")
    while True:
        command = speech_recognition_module.listen(cmd=True)
        if command == 'exit' or command == 'goodbye':
            text_to_speech_module.speak("Goodbye!")
            break
        response = assis.process_assistant_commands(command)
        text_to_speech_module.speak(response)