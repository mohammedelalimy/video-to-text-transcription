from flask import Flask, request, jsonify, redirect, url_for, Response
import os
from moviepy.editor import VideoFileClip
import whisper
import json

app = Flask(__name__)

# Configure the maximum content length for uploads (500 MB)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 500  # 500 MB limit

# Load the Whisper model
model = whisper.load_model("base")

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload Video</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            h1 {
                color: #333;  /* Set the color for the heading */
            }
            p {
                color: #555;  /* Set the color for the paragraph text */
            }
            form {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Upload a Video for Transcription</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="video" accept="video/*" required>
            <button type="submit">Upload</button>
        </form>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Ensure the uploads directory exists
    os.makedirs('uploads', exist_ok=True)

    # Save the video file
    video_path = os.path.join('uploads', video_file.filename)
    video_file.save(video_path)

    try:
        # Extract audio from the video
        audio_path = extract_audio(video_path)
        # Transcribe the audio
        transcript = transcribe_audio(audio_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    json_response = json.dumps({"transcript": transcript}, indent=4)
    styled_response = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Transcription Result</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                padding: 20px;
            }}
            pre {{
                background-color: #272822;
                color: #f8f8f2;
                padding: 20px;
                border-radius: 8px;
                overflow: auto;
            }}
        </style>
    </head>
    <body>
        <h1>Transcription Result</h1>
        <pre>{json_response}</pre>
    </body>
    </html>
    """
    return Response(styled_response, mimetype='text/html')

def extract_audio(video_path):
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    try:
        # Use a temporary file to reduce the load on memory
        with VideoFileClip(video_path) as video:
            video.audio.write_audiofile(audio_path)
    except Exception as e:
        raise RuntimeError(f"Error extracting audio: {e}")
    return audio_path

def transcribe_audio(audio_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at {audio_path}")

    try:
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        raise RuntimeError(f"Error during transcription: {e}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7860)
