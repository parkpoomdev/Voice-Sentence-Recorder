import os
import base64
import io
import zipfile
import re
import wave
import struct
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__))

def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def create_silence(duration_seconds, sample_rate=16000):
    num_samples = int(duration_seconds * sample_rate)
    return np.zeros(num_samples, dtype=np.int16)

def combine_audio_clips(audio_clips, gap_seconds, sample_rate=16000):
    silence = create_silence(gap_seconds, sample_rate)
    result = np.array([], dtype=np.int16)
    
    for clip in audio_clips:
        result = np.concatenate([result, clip, silence])
    
    return result

def save_wav_file(audio_data, filepath, sample_rate=16000):
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

def read_wav_from_bytes(audio_bytes):
    buffer = io.BytesIO(audio_bytes)
    with wave.open(buffer, 'rb') as wav_file:
        num_frames = wav_file.getnframes()
        audio_data = wav_file.readframes(num_frames)
        sample_rate = wav_file.getframerate()
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    return audio_array

def decode_audio_b64(audio_b64):
    if not audio_b64 or not isinstance(audio_b64, str):
        return None

    payload = audio_b64.strip()
    if payload.startswith('data:'):
        comma_index = payload.find(',')
        if comma_index == -1:
            return None
        payload = payload[comma_index + 1:]

    try:
        return base64.b64decode(payload)
    except Exception:
        return None

def clip_with_trim(audio_array, trim_info, sample_rate=16000):
    if not isinstance(trim_info, dict):
        return audio_array

    try:
        start_sec = float(trim_info.get('start', 0.0))
    except Exception:
        start_sec = 0.0

    try:
        end_sec = float(trim_info.get('end', len(audio_array) / sample_rate))
    except Exception:
        end_sec = len(audio_array) / sample_rate

    start_sec = max(0.0, start_sec)
    end_sec = max(start_sec, end_sec)

    start_idx = int(start_sec * sample_rate)
    end_idx = int(end_sec * sample_rate)

    start_idx = min(start_idx, len(audio_array))
    end_idx = min(end_idx, len(audio_array))

    if end_idx <= start_idx:
        return np.array([], dtype=np.int16)

    return audio_array[start_idx:end_idx]

def wav_bytes_from_array(audio_array, sample_rate=16000):
    buffer = io.BytesIO()
    with wave.open(buffer, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_array.tobytes())
    return buffer.getvalue()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/split', methods=['POST'])
def split_text():
    data = request.json
    text = data.get('text', '')
    sentences = split_sentences(text)
    return jsonify({'sentences': sentences})

@app.route('/api/save_audio', methods=['POST'])
def save_audio():
    data = request.json
    audio_data = data.get('audio', '')
    index = data.get('index', 0)
    
    if not audio_data:
        return jsonify({'success': False, 'error': 'No audio data'}), 400
    
    audio_bytes = decode_audio_b64(audio_data)
    if audio_bytes is None:
        return jsonify({'success': False, 'error': 'Invalid audio data'}), 400
    
    filename = f'sentences_voice_{index + 1}.wav'
    filepath = os.path.join(AUDIO_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(audio_bytes)
    
    return jsonify({'success': True, 'filename': filename})

@app.route('/api/export_individual', methods=['POST'])
def export_individual():
    data = request.json
    audios = data.get('audios', [])
    trims = data.get('trims', [])
    
    if not audios:
        return jsonify({'success': False, 'error': 'No audio data'}), 400
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, audio_b64 in enumerate(audios):
            if audio_b64:
                audio_bytes = decode_audio_b64(audio_b64)
                if audio_bytes is None:
                    continue
                trim_info = trims[i] if i < len(trims) else None
                if isinstance(trim_info, dict):
                    try:
                        audio_clip = read_wav_from_bytes(audio_bytes)
                        audio_clip = clip_with_trim(audio_clip, trim_info)
                        if len(audio_clip) == 0:
                            continue
                        audio_bytes = wav_bytes_from_array(audio_clip)
                    except Exception:
                        continue
                filename = f'sentences_voice_{i + 1}.wav'
                zf.writestr(filename, audio_bytes)
    
    zip_buffer.seek(0)
    
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='sentences_voice.zip'
    )

@app.route('/api/export_combined', methods=['POST'])
def export_combined():
    data = request.json
    audios = data.get('audios', [])
    trims = data.get('trims', [])
    gap_seconds = float(data.get('gap', 1.0))
    
    if not audios:
        return jsonify({'success': False, 'error': 'No audio data'}), 400
    
    audio_clips = []
    for i, audio_b64 in enumerate(audios):
        if audio_b64 and isinstance(audio_b64, str) and len(audio_b64) > 0:
            audio_bytes = decode_audio_b64(audio_b64)
            if audio_bytes is None:
                continue
            try:
                audio_clip = read_wav_from_bytes(audio_bytes)
                trim_info = trims[i] if i < len(trims) else None
                audio_clip = clip_with_trim(audio_clip, trim_info)
                if len(audio_clip) == 0:
                    continue
                audio_clips.append(audio_clip)
            except Exception:
                continue
    
    if not audio_clips:
        return jsonify({'success': False, 'error': 'No valid WAV audio found. Please re-record and try again.'}), 400
    
    combined = combine_audio_clips(audio_clips, gap_seconds)
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(combined.tobytes())
    
    buffer.seek(0)
    
    if gap_seconds == 0:
        gap_str = '0'
    else:
        gap_str = str(gap_seconds).replace('.', '')
    filename = f'sentences_all_{gap_str}.wav'
    filepath = os.path.join(AUDIO_DIR, filename)
    
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return send_file(
        buffer,
        mimetype='audio/wav',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/export_all', methods=['POST'])
def export_all():
    data = request.json
    audios = data.get('audios', [])
    trims = data.get('trims', [])
    
    if not audios:
        return jsonify({'success': False, 'error': 'No audio data'}), 400
    
    for gap in [1.0, 0.8, 0.5, 0]:
        audio_clips = []
        for i, audio_b64 in enumerate(audios):
            if audio_b64 and isinstance(audio_b64, str) and len(audio_b64) > 0:
                audio_bytes = decode_audio_b64(audio_b64)
                if audio_bytes is None:
                    continue
                try:
                    audio_clip = read_wav_from_bytes(audio_bytes)
                    trim_info = trims[i] if i < len(trims) else None
                    audio_clip = clip_with_trim(audio_clip, trim_info)
                    if len(audio_clip) == 0:
                        continue
                    audio_clips.append(audio_clip)
                except Exception:
                    continue
        
        if audio_clips:
            combined = combine_audio_clips(audio_clips, gap)
            if gap == 0:
                gap_str = '0'
            else:
                gap_str = str(gap).replace('.', '')
            filename = f'sentences_all_{gap_str}.wav'
            filepath = os.path.join(AUDIO_DIR, filename)
            save_wav_file(combined, filepath)
    
    return jsonify({
        'success': True,
        'files': [
            'sentences_all_1.wav',
            'sentences_all_08.wav',
            'sentences_all_05.wav',
            'sentences_all_0.wav'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
