import speech_recognition as sr
import pyttsx3

class VoiceController:
    def __init__(self):
        try:
            self.recognizer = sr.Recognizer()
            self.tts_engine = pyttsx3.init()
            self.is_voice_enabled = True
        except Exception as e:
            print(f"Voice initialization failed: {e}")
            self.is_voice_enabled = False

    def toggle_voice(self, enabled):
        self.is_voice_enabled = enabled

    def speak(self, text):
        if not self.is_voice_enabled:
            return
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error in text-to-speech: {e}")

    def listen(self, timeout=5, phrase_time_limit=15):
        if not self.is_voice_enabled:
            return None
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                print("Recognizing...")
                return self.recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            return "Listening timed out."
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError as e:
            return f"Speech recognition service error: {e}"
        except Exception as e:
            return f"Microphone error: {e}"
        