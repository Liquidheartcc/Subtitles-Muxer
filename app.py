import os
import subprocess
import requests
from flask import Flask, request

app = Flask(__name__)

# Set up your Telegram bot token
TOKEN = os.environ.get('BOT_TOKEN')

# Define the endpoint for your bot
@app.route('/bot', methods=['POST'])
def bot():
    try:
        # Parse the incoming message
        print('Incoming message:', request.json)
        chat_id = request.json['message']['chat']['id']
        video_url = request.json['message']['video']['file_id']
        subtitle_url = request.json['message']['document']['file_id']
        
        # Download the video and subtitle files
        print('Downloading video:', video_url)
        video_file = download_file(video_url)
        print('Downloading subtitle:', subtitle_url)
        subtitle_file = download_file(subtitle_url)

        # Mux the subtitle into the video using FFmpeg
        print('Muxing video and subtitle')
        muxed_video_file = mux_subtitles(video_file, subtitle_file)

        # Upload the muxed video to Telegram
        print('Uploading video')
        upload_file(muxed_video_file, chat_id)

        return 'OK'
    
    except Exception as e:
        print('Error:', e)
        return 'Error'

# Download a file from Telegram using its file_id
def download_file(file_id):
    url = f'https://api.telegram.org/bot{TOKEN}/getFile'
    params = {'file_id': file_id}
    response = requests.get(url, params=params)
    file_path = response.json()['result']['file_path']
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'
    file_name = os.path.basename(file_path)
    response = requests.get(file_url)
    with open(file_name, 'wb') as f:
        f.write(response.content)
    print('File downloaded:', file_name)
    return file_name

# Mux a subtitle file into a video file using FFmpeg
def mux_subtitles(video_file, subtitle_file):
    muxed_video_file = 'muxed_video.mp4'
    subprocess.run(['ffmpeg', '-i', video_file, '-vf', f'subtitles={subtitle_file}', muxed_video_file])
    print('Video and subtitle muxed')
    return muxed_video_file

# Upload a file to Telegram using its file_path and chat_id
def upload_file(file_path, chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendVideo'
    files = {'video': open(file_path, 'rb')}
    params = {'chat_id': chat_id}
    response = requests.post(url, params=params, files=files)
    print('Video uploaded')
    return response.json()

if __name__ == '__main__':
    app.run()
