from gtts import gTTS
import pygame
import os
import time
import hashlib
import pyttsx3

class SpeechManager:
    def __init__(self, lang='id', fallback=True):
        self.lang = lang
        self.fallback = fallback
        self.cache_dir = "speech_cache"
        self.muted = False
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        pygame.mixer.init()
        
        # Initialize offline TTS engine as fallback
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
    def speak(self, text, speed=1.0, volume=1.0):
        if self.muted:
            return
            
        if not text:
            return
            
        # Create a unique filename based on the text and speed
        cache_key = f"{text}_{speed}"
        filename = hashlib.md5(cache_key.encode()).hexdigest() + ".mp3"
        filepath = os.path.join(self.cache_dir, filename)
        
        try:
            # Try online gTTS if file doesn't exist
            if not os.path.exists(filepath):
                # gTTS 'slow' parameter: True is slow, False is normal.
                # For higher speed (1.3x), gTTS doesn't support it directly.
                # We'll use slow=False for anything > 1.0.
                is_slow = speed < 1.0
                tts = gTTS(text=text, lang=self.lang, slow=is_slow)
                tts.save(filepath)
            
            # Play the audio
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(min(1.0, volume))
            pygame.mixer.music.play()
            
        except Exception as e:
            print(f"Online TTS Error: {e}")
            if self.fallback:
                print("Using offline fallback...")
                # pyttsx3 supports rate (speed)
                self.engine.setProperty('rate', int(150 * speed))
                self.engine.setProperty('volume', min(1.0, volume))
                self.engine.say(text)
                self.engine.runAndWait()

    def play_jokowi_meme(self):
        """Plays the special Jokowi meme audio file."""
        if self.muted: return
        
        filepath = os.path.join("SignLanguage_Speech_Translator", "assets", "hidup_jokowiiie.mp3")
        if not os.path.exists(filepath):
            # Fallback for when running from within the project dir
            filepath = os.path.join("assets", "hidup_jokowiiie.mp3")
            
        if os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(1.0) # Always full volume for the meme
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Meme Audio Playback Error: {e}")
        else:
            print("File audio Jokowi tidak ditemukan")
            # We will handle the overlay in main.py by checking return status or similar
            return False
        return True

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted

if __name__ == "__main__":
    sm = SpeechManager()
    sm.speak("Halo, assalamualaikum")
