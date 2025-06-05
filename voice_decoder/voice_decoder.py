"""This file implements voice recognizer pipeline"""

import tempfile

import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

class VoiceDecoder:
    """
    A class that provides voice interaction functionalities including wake word detection,
    speech-to-text conversion, and text-to-speech synthesis.
    """

    def __init__(self, language: str = "pt-br", wake_word: str = "Serena"):
        """
        Initializes the VoiceDecoder with language and wake word.

        :param language: Language code for speech recognition (default is 'pt-BR').
        :param wake_word: The word used to activate the assistant.
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.wake_word = wake_word.lower()

    def string_to_speech(self, text: str) -> None:
        """
        Converts a text string to speech and plays it using gTTS.

        :param text: The string to be spoken.
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text, lang='pt')
            tts.save(fp.name)
            audio = AudioSegment.from_file(fp.name, format="mp3")
            play(audio)

    def audio_to_string(self) -> str:
        """
        Listens from the microphone and converts the audio to a text string.

        :return: The recognized text or an empty string if recognition fails.
        """
        with sr.Microphone() as source:
            print("Listening for a command...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.2)
            audio = self.recognizer.listen(source, phrase_time_limit=6)

        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return ""
        except sr.RequestError as e:
            print(f"Error with the recognition service: {e}")
            return ""

    def listen_for_wake_word(self) -> None:
        """
        Continuously listens for the wake word. Once detected, listens for a command and responds.
        """
        print("Waiting for wake word...")

        while True:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.2)
                try:
                    audio = self.recognizer.listen(source, timeout=2)
                    phrase = self.recognizer.recognize_google(
                        audio, language=self.language
                    ).lower()
                    print(f"Heard: {phrase}")

                    if self.wake_word in phrase:
                        print("Wake word detected!")
                        self.string_to_speech("estou ouvindo no que posso ajudar")
                        return True
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Connection error: {e}")
