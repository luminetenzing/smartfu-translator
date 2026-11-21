import io
import requests
from deep_translator import GoogleTranslator
from gtts import gTTS
from langdetect import DetectorFactory, detect
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0


def load_languages():
    raw = GoogleTranslator().get_supported_languages(as_dict=True)
    name_to_code = {k.title(): v for k, v in raw.items()}
    code_to_name = {v.lower(): k.title() for k, v in raw.items()}
    return name_to_code, code_to_name


def _gtx_translate(text, target):
    res = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": "auto", "tl": target, "dt": "t", "q": text},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=8,
    )
    res.raise_for_status()
    data = res.json()
    translated = "".join(chunk[0] for chunk in data[0] if chunk and chunk[0])
    detected = data[2] if len(data) > 2 and isinstance(data[2], str) else None
    return translated, detected


def _mymemory_translate(text, src, target):
    if src.lower() == target.lower():
        return text
    res = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": text, "langpair": f"{src}|{target}"},
        timeout=8,
    )
    res.raise_for_status()
    payload = res.json()
    if payload.get("responseStatus") != 200:
        raise ValueError("mymemory error")
    return payload["responseData"]["translatedText"]


def translate(text, target_code):
    # Try Google GTX first since deep-translator's scraper gets rate-limited easily
    try:
        out, detected = _gtx_translate(text, target_code)
        if out:
            return out, detected, "Google GTX"
    except Exception:
        pass

    try:
        src_code = detect(text)
    except LangDetectException:
        src_code = "en"

    try:
        out = _mymemory_translate(text, src_code, target_code)
        if out:
            return out, src_code, "MyMemory"
    except Exception:
        pass

    out = GoogleTranslator(source="auto", target=target_code).translate(text)
    return out, src_code, "DeepTranslator"


def text_to_speech(text, lang_code):
    buf = io.BytesIO()
    gTTS(text=text, lang=lang_code).write_to_fp(buf)
    buf.seek(0)
    return buf