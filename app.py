from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters
from telegram import Update
import requests
from moviepy.video.VideoClip import VideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

# Create a new Flask application
app = Flask(__name__)

# Set up the Telegram bot
dispatcher = Dispatcher(None, None)

# Define a handler function for handling Telegram messages
def handle_message(update: Update, context: Dispatcher):
    # Get the chat ID and message text from the update object
    chat_id = update.effective_chat.id
    message_text = update.message.text

    # Download the video file and subtitle file from the URLs in the message text
    video_url, subtitle_url = message_text.split()
    video_file = requests.get(video_url).content
    subtitle_file = requests.get(subtitle_url).text

    # Mux the subtitles into the video file
    video_clip = VideoClip(video_file)
    subtitle_clip = SubtitlesClip(subtitle_file)
    subtitle_clip = subtitle_clip.set_start(0).set_end(video_clip.duration)
    result_clip = video_clip.set_audio(None).set_subclip(0, video_clip.duration).set_fps(30).set_audio(video_clip.audio).set_subtitles([subtitle_clip])
    result_file = "result.mp4"
    result_clip.write_videofile(result_file, codec="libx264", temp_audiofile="temp-audio.m4a", remove_temp=True, audio_codec="aac")

    # Send the result file to the user
    with open(result_file, "rb") as f:
        context.bot.send_video(chat_id=chat_id, video=f)

# Set up the Telegram message handler
dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

# Define a route for handling incoming webhook requests from Telegram
@app.route("/<token>", methods=["POST"])
def webhook(token):
    # Process the incoming update
    update = Update.de_json(request.get_json(force=True), dispatcher.bot)
    dispatcher.process_update(update)
    return "ok"

if __name__ == "__main__":
    # Start the Flask application
    app.run()
