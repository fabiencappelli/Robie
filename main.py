import atexit
import json
import subprocess
import time
import wave
from pathlib import Path

import board
import adafruit_dotstar
import numpy as np
import openwakeword
import sounddevice as sd
from openwakeword.model import Model
from vosk import KaldiRecognizer, Model as VoskModel

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
AUDIO_DEVICE_INDEX = None

RECORD_SECONDS = 4
WAKE_THRESHOLD = 0.95
CONSECUTIVE_HITS_REQUIRED = 3
REFRACTORY_SECONDS = 10.0

BRIGHTNESS = 0.03
COLOR_OFF = (0, 0, 0)
COLOR_LISTENING = (255, 0, 0)
COLOR_THINKING = (180, 120, 0)

WAKEWORD_MODEL_NAME = "hey_mycroft_v0.1.tflite"
RECORDED_WAV = "last_command.wav"
TTS_WAV = "/tmp/robie_tts.wav"

# À adapter selon l'endroit où tu as mis ton modèle Vosk FR
VOSK_MODEL_PATH = Path("models/vosk-model-small-fr-0.22")

dots = adafruit_dotstar.DotStar(board.D6, board.D5, 3, brightness=BRIGHTNESS)


def set_led(color):
    dots.fill(color)


def cleanup():
    set_led(COLOR_OFF)


atexit.register(cleanup)


def record_wav(filename=RECORDED_WAV, seconds=4, samplerate=16000, device=None):
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
        wf.setsampwidth(2)  # int16 = 2 bytes
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())


def make_wake_model():
    openwakeword.utils.download_models()
    model_path = str(
        Path(openwakeword.__file__).parent
        / "resources"
        / "models"
        / WAKEWORD_MODEL_NAME
    )
    return Model(wakeword_models=[model_path])


def make_vosk_model():
    if not VOSK_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Modèle Vosk introuvable : {VOSK_MODEL_PATH}\n"
            "Télécharge un modèle FR et corrige VOSK_MODEL_PATH."
        )
    return VoskModel(str(VOSK_MODEL_PATH))


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


def transcribe_wav(filename, vosk_model):
    with wave.open(filename, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()

        if n_channels != 1:
            raise ValueError(f"Le WAV doit être mono, ici: {n_channels} canaux")
        if sampwidth != 2:
            raise ValueError(f"Le WAV doit être en int16, ici: {sampwidth} octets")
        if framerate != SAMPLE_RATE:
            raise ValueError(
                f"Le WAV doit être à {SAMPLE_RATE} Hz, ici: {framerate} Hz"
            )

        recognizer = KaldiRecognizer(vosk_model, framerate)
        recognizer.SetWords(False)

        while True:
            data = wf.readframes(4000)
            if not data:
                break
            recognizer.AcceptWaveform(data)

        final_result = json.loads(recognizer.FinalResult())
        text = final_result.get("text", "").strip()
        return text


def speak_text(text):
    safe_text = text.strip()
    if not safe_text:
        safe_text = "Je n'ai rien compris."

    print(f"TTS -> {safe_text}")

    subprocess.run(
        ["pico2wave", "-l", "fr-FR", "-w", TTS_WAV, safe_text],
        check=True,
    )
    subprocess.run(["aplay", TTS_WAV], check=True)


def main():
    set_led(COLOR_OFF)

    wake_model = make_wake_model()
    vosk_model = make_vosk_model()

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

            predictions = wake_model.predict(audio)
            score = max(predictions.values()) if predictions else 0.0

            if score >= WAKE_THRESHOLD:
                consecutive_hits += 1
            else:
                consecutive_hits = 0

            if consecutive_hits >= CONSECUTIVE_HITS_REQUIRED:
                print(f"Wake détecté (score={score:.3f})")
                consecutive_hits = 0
                refractory_until = time.time() + REFRACTORY_SECONDS

                stream.stop()
                stream.close()

                try:
                    set_led(COLOR_LISTENING)
                    time.sleep(0.1)

                    record_wav(
                        filename=RECORDED_WAV,
                        seconds=RECORD_SECONDS,
                        samplerate=SAMPLE_RATE,
                        device=AUDIO_DEVICE_INDEX,
                    )

                    set_led(COLOR_THINKING)

                    text = transcribe_wav(RECORDED_WAV, vosk_model)
                    print(f"Transcription : {text!r}")

                    # Petite pause pour lisibilité UX
                    time.sleep(0.2)

                    spoken_text = (
                        f"Tu as dit : {text}" if text else "Je n'ai rien compris."
                    )
                    speak_text(spoken_text)

                    set_led(COLOR_OFF)
                    print("Retour en veille.")

                except Exception as exc:
                    print(f"Erreur pendant traitement : {exc}")
                    set_led(COLOR_OFF)

                finally:
                    wake_model = make_wake_model()
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
