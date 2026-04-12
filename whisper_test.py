import json
import wave
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-model-small-fr-0.22"  # adapte si le nom diffère
AUDIO_PATH = "last_command.wav"

def main():
    wf = wave.open(AUDIO_PATH, "rb")

    if wf.getnchannels() != 1:
        raise ValueError("Le fichier audio doit être mono.")
    if wf.getsampwidth() != 2:
        raise ValueError("Le fichier audio doit être en PCM 16 bits.")
    if wf.getcomptype() != "NONE":
        raise ValueError("Le fichier audio doit être non compressé (WAV PCM).")

    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, wf.getframerate())

    final_text_parts = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").strip()
            if text:
                final_text_parts.append(text)

    final_result = json.loads(rec.FinalResult())
    final_text = final_result.get("text", "").strip()
    if final_text:
        final_text_parts.append(final_text)

    print("Transcription :")
    print(" ".join(final_text_parts).strip())

if __name__ == "__main__":
    main()