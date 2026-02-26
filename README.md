# Voice Sentence Recorder

<img width="1920" height="1620" alt="Voice Sentence Recorder UI" src="https://github.com/user-attachments/assets/3025b4a2-ecf2-4531-848d-065d277af65c" />

Voice Sentence Recorder is a local web app for turning long text into sentence-by-sentence recording cards.
You can record each sentence, trim audio with a waveform timeline, preview the result, and export WAV files.

## What it does

- Split pasted text into sentence cards
- Record one audio clip per sentence
- Edit each clip using timeline trim handles (left/right)
- Play, pause/resume, and stop per sentence
- Preview combined output before downloading
- Export:
  - Individual WAV files in ZIP (`sentences_voice_1.wav`, `sentences_voice_2.wav`, ...)
  - Combined WAV with gaps (`1s`, `0.8s`, `0.5s`)
  - Combined WAV with no gap
  - Batch export all combined variants to local project folder

## Tech stack

- Backend: Python + Flask
- Frontend: HTML, CSS, Vanilla JavaScript
- Audio processing: NumPy + Python `wave` module

## Run locally

1. Install dependencies:

```bash
pip install flask numpy
```

2. Start app:

```bash
python app.py
```

3. Open in browser:

`http://127.0.0.1:5000`

## Basic workflow

1. Paste text and click **Split Text**
2. Record each sentence card
3. Adjust trim in the waveform timeline if needed
4. Preview single cards and combined output
5. Export the audio format you need
