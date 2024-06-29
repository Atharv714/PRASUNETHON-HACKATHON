from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import re
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import newgender


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

app = Flask(__name__)

if newgender.essential()=='Male':
    avaj = 'nova'

else :
    avaj = 'echo'

def send_message(message):
    if not isinstance(message,str):
        raise ValueError("Message must be String")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [
            {
                "role" : "system", "content": "You are a doctor that analyze patient symptoms and give them advisory."
            },

            {"role": "user", "content": message}
        ],

        max_tokens=100,
        temperature=0.7
    )

    return response.choices[0].message.content

import time
def convert_to_speech(text):
    speech_file_path =  "static/output.mp3"
    
    response = client.audio.speech.create(
        model="tts-1",
        voice=avaj,
        input=text
    )

    # generated audio save
    response.stream_to_file(speech_file_path)

    # Return the URL to the saved audio with a timestamp as a query parameter
    return f"/output.mp3?{int(time.time())}"

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/save-transcription', methods=['POST'])
def save_transcription():
    data = request.get_json()
    transcription = data['transcription']
    with open('transcription.txt', 'w') as f:
        f.write(transcription)
    # chat gpt ka response
    chat_response = send_message(transcription)

    # response to speech aur uska url
    audio_url = convert_to_speech(chat_response)
    return jsonify({'message': 'Transcription saved successfully', 'chat_response': chat_response, 'audio_url': audio_url})

@app.route('/output.mp3')
def serve_audio():
    return send_from_directory('static', 'output.mp3')

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
