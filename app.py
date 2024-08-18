from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import json

app = Flask(__name__)
DOWNLOADS_DIR = 'static/obrik/'  # Folder named 'obrik' to save downloads

# Replace with your actual proxy details
PROXY = 'http://123.45.67.89:8080'

def _progress_hook(d, progress_file):
    if d['status'] == 'downloading':
        progress_data = {
            'title': d.get('filename', 'Unknown Title'),
            'progress': d.get('_percent_str', '0%'),
            'current': d.get('_downloaded_bytes_str', '0'),
            'total': d.get('_total_bytes_str', '0')
        }
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/download-video', methods=['POST'])
def download_video():
    video_url = request.form.get('video_url').strip()
    quality = request.form.get('quality').strip()

    if not video_url:
        return jsonify({'status': 'error', 'message': 'Please provide a valid YouTube video URL.'})

    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    progress_file = os.path.join(DOWNLOADS_DIR, 'progress_video.json')

    ydl_opts = {
        'format': quality,
        'outtmpl': f'{DOWNLOADS_DIR}/%(title)s.%(ext)s',
        'progress_hooks': [lambda d: _progress_hook(d, progress_file)],
        'proxy': PROXY  # Added proxy support
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return jsonify({'status': 'completed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download-playlist', methods=['POST'])
def download_playlist():
    playlist_url = request.form.get('playlist_url').strip()
    quality = request.form.get('quality').strip()

    if not playlist_url:
        return jsonify({'status': 'error', 'message': 'Please provide a valid YouTube playlist URL.'})

    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    progress_file = os.path.join(DOWNLOADS_DIR, 'progress_playlist.json')

    ydl_opts = {
        'format': quality,
        'outtmpl': f'{DOWNLOADS_DIR}/%(playlist)s/%(title)s.%(ext)s',
        'noplaylist': False,
        'progress_hooks': [lambda d: _progress_hook(d, progress_file)],
        'proxy': PROXY  # Added proxy support
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        return jsonify({'status': 'completed'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/check-progress/<progress_type>')
def check_progress(progress_type):
    progress_file = os.path.join(DOWNLOADS_DIR, f'progress_{progress_type}.json')
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        return jsonify({'progress': progress})
    return jsonify({'progress': 'No progress available'})

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(DOWNLOADS_DIR, filename)


