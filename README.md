# smartfu translator

A lightweight web translator built with Python and Streamlit. It detects the source language automatically, translates text across supported languages, and generates audio pronunciation for the translated result.

**Live Demo:** [Try smartfu translator online](https://smartfu-translator.streamlit.app)

## Key Features
- **Automatic Language Detection:** Detects input language automatically without manual selection.
- **Multi-Provider Fallback:** Uses Google GTX endpoint as the primary provider, with MyMemory API and `deep-translator` as backups to prevent IP rate-limit errors.
- **Text-to-Speech (TTS):** Generates playable MP3 audio directly in the browser using `gTTS`.
- **Session History:** Tracks recent translations during the current session.
- **Custom UI:** Styled with external CSS (`style.css`) for a glassmorphism layout.

## Project Structure
- `app.py` – Streamlit user interface and state management.
- `translator.py` – Translation pipeline, fallback handling, and audio generation.
- `style.css` – Custom layout styling.
- `requirements.txt` – Python dependencies.

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
