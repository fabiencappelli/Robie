import subprocess
from pathlib import Path


def speak(text: str, wav_path: str = "/tmp/robie_tts.wav") -> None:
    output = Path(wav_path)

    subprocess.run(
        ["pico2wave", "-l", "fr-FR", "-w", str(output), text],
        check=True,
    )

    subprocess.run(
        ["aplay", str(output)],
        check=True,
    )
