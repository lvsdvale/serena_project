import time

from voice_decoder import VoiceDecoder

if __name__ == "__main__":
    decoder = VoiceDecoder()
    while not decoder.listen_for_wake_word():
        pass
    decoder.string_to_speech("esta na hora de tomar seu dipirona")
