import speech_recognition as sr
import threading
import time

class VoiceController:
    def __init__(self, wake_phrase="hi my assistant", command_phrase="open the app"):
        self.wake_phrase = wake_phrase.lower()
        self.command_phrase = command_phrase.lower()
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.wake_detected = False
        self.command_ready = False
        self.stop_listening = False
        
        # Audio tuning
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def start_background_listening(self):
        """Starts a background thread to listen for voice commands."""
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _listen_loop(self):
        print("Voice listener started. Say 'Hi my assistant' to begin.")
        while not self.stop_listening:
            with self.microphone as source:
                try:
                    # Brief timeout to keep the loop responsive
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Heard: {text}")
                    
                    if self.wake_phrase in text:
                        print("Wake phrase detected!")
                        self.wake_detected = True
                        # Immediately check if command is also in the same phrase
                        if self.command_phrase in text:
                            print("Command detected!")
                            self.command_ready = True
                    elif self.wake_detected and self.command_phrase in text:
                        print("Command detected!")
                        self.command_ready = True
                        
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"Voice Error: {e}")
                    continue

    def reset_state(self):
        """Resets the detection flags after a command is executed."""
        self.wake_detected = False
        self.command_ready = False

if __name__ == "__main__":
    # Test
    vc = VoiceController()
    vc.start_background_listening()
    try:
        while True:
            if vc.command_ready:
                print(">>> VOICE COMMAND READY! Waiting for gesture...")
                time.sleep(5)
                vc.reset_state()
            time.sleep(1)
    except KeyboardInterrupt:
        vc.stop_listening = True
