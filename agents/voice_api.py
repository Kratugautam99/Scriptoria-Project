from vosk import Model
import os
import wave
import json
from vosk import KaldiRecognizer
import io

_MODEL = None

def _load_model():
    global _MODEL
    if _MODEL:
        return _MODEL

    model_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "data", "model", "vosk-model-small-en-us-0.15"
    )
    model_dir = os.path.normpath(model_dir)

    if not os.path.isdir(model_dir):
        raise FileNotFoundError(
            f"VOSK model not found at {model_dir}. "
            "Download from https://alphacephei.com/vosk/models and unzip it there."
        )

    _MODEL = Model(model_dir)
    return _MODEL



def text_to_speech(text: str):
    import pyttsx3
    engine = pyttsx3.init(driverName="espeak")  
    engine.setProperty("voice", "en")           
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
