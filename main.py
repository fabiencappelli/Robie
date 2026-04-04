import atexit
import random
import subprocess
import time
import wave
from pathlib import Path

import board
import adafruit_dotstar
import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
AUDIO_DEVICE_INDEX = None

RECORD_SECONDS = 4
WAKE_THRESHOLD = 0.95
CONSECUTIVE_HITS_REQUIRED = 3
REFRACTORY_SECONDS = 10.0

ASSETS_DIR = Path("assets")

BRIGHTNESS = 0.03
COLOR_OFF = (0, 0, 0)
COLOR_LISTENING = (255, 0, 0)
COLOR_THINKING = (180, 120, 0)

dots = adafruit_dotstar.DotStar(board.D6, board.D5, 3, brightness=BRIGHTNESS)

def set_led(color):
    dots.fill(color)

def cleanup():
    set_led(COLOR_OFF)

atexit.register(cleanup)

def play_random_mp3():
    files = sorted(ASSETS_DIR.glob("*.mp3"))
    if not files:
        print("Aucun mp3 trouvé dans assets/")
        return
    chosen = random.choice(files)
    print(f"Lecture : {chosen}")
    subprocess.run(["mpg123", "-q", str(chosen)], check=False)

def record_wav(filename="last_command.wav", seconds=4, samplerate=16000, device=None):
    print(f"Enregistrement {seconds}s -> {filename}")
    audio = sd.rec(
        int(seconds * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="int16",
        device=device,
    )
    sd.wait()

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())

def make_model():
    # Téléchargement one-shot déjà fait chez toi, mais ça ne gêne pas
    openwakeword.utils.download_models()

    # Charge un seul modèle au lieu de tous
    model_path = str(Path(openwakeword.__file__).parent / "resources" / "models" / "hey_mycroft_v0.1.tflite")
    return Model(wakeword_models=[model_path])

def open_stream():
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SIZE,
        device=AUDIO_DEVICE_INDEX,
    )
    stream.start()
    return stream

def main():
    set_led(COLOR_OFF)
    model = make_model()
    print("Robie en veille. LEDs éteintes.")

    stream = open_stream()
    consecutive_hits = 0
    refractory_until = 0.0

    try:
        while True:
            audio, _ = stream.read(CHUNK_SIZE)
            audio = np.frombuffer(audio, dtype=np.int16)

            now = time.time()
            if now < refractory_until:
                continue

            predictions = model.predict(audio)
            score = max(predictions.values()) if predictions else 0.0

            if score >= WAKE_THRESHOLD:
                consecutive_hits += 1
            else:
                consecutive_hits = 0

            if consecutive_hits >= CONSECUTIVE_HITS_REQUIRED:
                print(f"Wake détecté (score={score:.3f})")
                consecutive_hits = 0
                refractory_until = time.time() + REFRACTORY_SECONDS

                # Coupe l'écoute wake pendant l'action
                stream.stop()
                stream.close()

                try:
                    set_led(COLOR_LISTENING)
                    time.sleep(0.1)

                    record_wav(
                        filename="last_command.wav",
                        seconds=RECORD_SECONDS,
                        samplerate=SAMPLE_RATE,
                        device=AUDIO_DEVICE_INDEX,
                    )

                    set_led(COLOR_THINKING)
                    time.sleep(0.8)

                    play_random_mp3()

                    set_led(COLOR_OFF)
                    print("Retour en veille.")

                finally:
                    # Repart d'un état propre
                    model = make_model()
                    stream = open_stream()

    except KeyboardInterrupt:
        print("\nArrêt demandé.")
    finally:
        try:
            stream.stop()
            stream.close()
        except Exception:
            pass
        set_led(COLOR_OFF)

if __name__ == "__main__":
    main()