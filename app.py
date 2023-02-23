import os
import subprocess
import requests
from flask import Flask, request

app = Flask(__name__)

# Set up your Telegram bot token
TOKEN = os.environ.get('TOKEN')
if TOKEN is None:
    print("Please set the TOKEN environment variable.")
    exit(1)

# Define the endpoint for your bot
@app.route('/bot', methods=['POST'])
def bot():

    # Parse the incoming message
    message = request.json['message']
    chat_id = message['chat']['id']

    # Send a welcome message to the user
    if 'text' in message and message['text'] == '/start':
        send_message(chat_id, 'Welcome to my subtitle muxing bot! Send me a video file and a subtitle file, and I will mux the subtitle into the video.')

    # Check if the message contains a video and a subtitle
    if 'video' in message and 'document' in message:
        video_url = message['video']['file_id']
        subtitle_url = message['document']['file_id']

        # Download the video and subtitle files
        video_file = download_file(video_url)
        subtitle_file = download_file(subtitle_url)

        # Mux the subtitle into the video using FFmpeg
        muxed_video_file = mux_subtitles(video_file, subtitle_file)

        # Upload the muxed video to Telegram
        upload_file(muxed_video_file, chat_id)

    return 'OK'

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
    return file_name

# Mux a subtitle file into a video file using FFmpeg
def mux_subtitles(video_file, subtitle_file):
    muxed_video_file = 'muxed_video.mp4'
    subprocess.run(['ffmpeg', '-i', video_file, '-vf', f'subtitles={subtitle_file}', muxed_video_file])
    return muxed_video_file

# Upload a file to Telegram using its file_path and chat_id
def upload_file(file_path, chat_id):
    url = f'https://api.telegram.org/bot{TOKEN}/sendVideo'
    files = {'video': open(file_path, 'rb')}
    params = {'chat_id': chat_id}
    response = requests.post(url, params=params, files=files)
    return response.json()

# Send a message to a Telegram chat using the bot
def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    params = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, params=params)
    return response.json()

if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False), port=int(os.environ.get('PORT', 5000)))
