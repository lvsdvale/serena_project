import tempfile
import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


class VoiceDecoder:
    """
    A class that provides voice interaction functionalities including wake word detection,
    speech-to-text conversion, and text-to-speech synthesis.
    """

    def __init__(
        self,
        language: str = "pt-br",
        light_controller=None,
        wake_word: str = "Serena",
        mic_name_hint: str = "USB2.0"  # Nome parcial do microfone USB
    ):
        """
        Initializes the VoiceDecoder with language and wake word.

        :param language: Language code for speech recognition (default is 'pt-BR').
        :param wake_word: The word used to activate the assistant.
        :param light_controller: the light controller to assist user.
        :param mic_name_hint: Partial name of the microphone to auto-select.
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.wake_word = wake_word.lower()
        self.light_controller = light_controller
        self.device_index = self.find_device_index(mic_name_hint)

    def find_device_index(self, target_substring: str) -> int:
        """
        Finds the index of a microphone based on a partial name match.

        :param target_substring: A substring to match microphone name (e.g. "USB").
        :return: The index of the matching microphone device.
        """
        mic_names = sr.Microphone.list_microphone_names()
        for index, name in enumerate(mic_names):
            if target_substring.lower() in name.lower():
                print(f"[INFO] Microfone encontrado: {name} (index {index})")
                return index
        raise RuntimeError(f"Microfone contendo '{target_substring}' não encontrado.")

    def string_to_speech(self, text: str) -> None:
        """Converts a text string to speech and plays it using gTTS."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text, lang="pt")
            tts.save(fp.name)

        try:
            audio = AudioSegment.from_file(fp.name, format="mp3")
            play(audio)
        finally:
            os.remove(fp.name)

    def audio_to_string(self) -> str:
        """Listens from the microphone and converts the audio to a text string."""
        with sr.Microphone(device_index=self.device_index) as source:
            print(f"[INFO] Usando microfone: {sr.Microphone.list_microphone_names()[self.device_index]}")
            print("Listening for a command...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.2)

            if self.light_controller:
                self.light_controller.green_on()

            audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=6)

            if self.light_controller:
                self.light_controller.blue_on()

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

    def listen_for_wake_word(self) -> bool:
        """Continuously listens for the wake word. Once detected, listens for a command and responds."""
        print("Waiting for wake word...")

        try:
            while True:
                with sr.Microphone(device_index=self.device_index) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.2)
                    try:
                        audio = self.recognizer.listen(source, timeout=2)
                        phrase = self.recognizer.recognize_google(
                            audio, language=self.language
                        ).lower()
                        print(f"Heard: {phrase}")

                        if self.wake_word in phrase:
                            print("Wake word detected!")
                            if self.light_controller:
                                self.light_controller.green_on()
                                self.light_controller.blue_on()
                            self.string_to_speech("estou ouvindo, no que posso ajudar?")
                            return True
                    except sr.WaitTimeoutError:
                        pass
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        print(f"Connection error: {e}")
        except KeyboardInterrupt:
            print("Interrompido pelo usuário.")
            return False
