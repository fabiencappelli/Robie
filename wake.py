import time
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280   # ~80 ms � 16 kHz
AUDIO_DEVICE_INDEX = None  # remplace si besoin

model = Model()
print("Mod�les charg�s :", list(model.models.keys()))

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    blocksize=CHUNK_SIZE,
    device=AUDIO_DEVICE_INDEX,
) as stream:
    print("�coute en cours...")
    while True:
        audio, _ = stream.read(CHUNK_SIZE)
        audio = np.frombuffer(audio, dtype=np.int16)
        predictions = model.predict(audio)

        # Affiche seulement les scores un peu int�ressants
        interesting = {k: round(v, 3) for k, v in predictions.items() if v > 0.2}
        if interesting:
            print(interesting)

        time.sleep(0.01)