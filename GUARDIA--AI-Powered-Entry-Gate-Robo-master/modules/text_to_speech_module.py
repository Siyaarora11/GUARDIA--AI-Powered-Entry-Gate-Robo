# modules/text_to_speech_module.py

import pyttsx3
import azure.cognitiveservices.speech as speechsdk
from config import SPEECH_KEY, SPEECH_REGION, SPEECH_VOICE

class TextToSpeechModule:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)  # Speech rate
        self.engine.setProperty('volume', 1)
        self.engine.setProperty('voice', self.get_female_voice)

    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.startLoop(False)
            self.engine.iterate()
            self.engine.endLoop()
        except:
            pass
    
    @property
    def get_female_voice(self):
        voices = self.engine.getProperty('voices')
        return voices[1].id


class AzureTextToSpeechModule:
    def __init__(self):
        self.speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_config.speech_synthesis_voice_name = SPEECH_VOICE
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)

    def speak(self, text):
        speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")
