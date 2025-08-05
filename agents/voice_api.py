from vosk import Model
import os
import wave
import json
from vosk import KaldiRecognizer
import io

_MODEL = None

def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    base_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(base_dir, os.pardir))
    model_dir = os.path.join(project_root, "data","model", "vosk-model-small-en-us-0.15")

    if not os.path.isdir(model_dir):
        raise FileNotFoundError(
            f"VOSK model not found at {model_dir!r}. "
            "Please download and unzip the model into models/vosk-model-small-en-us-0.15"
        )

    _MODEL = Model(model_dir)
    return _MODEL


def text_to_speech(text: str):
    import pyttsx3
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def speech_to_text(wav_path_or_bytes) -> str:
    """
    Transcribe speech from a WAV file path or byte stream using VOSK.

    Args:
        wav_path_or_bytes (str | bytes): WAV file path or byte content.

    Returns:
        str: Transcribed text.
    """
    model = _load_model()

    if isinstance(wav_path_or_bytes, bytes):
        wf = wave.open(io.BytesIO(wav_path_or_bytes), "rb")
    elif isinstance(wav_path_or_bytes, str):
        wf = wave.open(wav_path_or_bytes, "rb")
    else:
        raise TypeError("Input must be a file path or bytes.")

    if wf.getnchannels() != 1 or wf.getframerate() != 16000:
        raise ValueError("WAV file must be mono and 16kHz for VOSK.")

    recognizer = KaldiRecognizer(model, wf.getframerate())
    transcript = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            res = json.loads(recognizer.Result())
            transcript += res.get("text", "") + " "

    final_res = json.loads(recognizer.FinalResult())
    transcript += final_res.get("text", "")
    return transcript.strip()
