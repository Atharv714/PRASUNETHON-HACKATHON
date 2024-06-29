from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import re
from openai import OpenAI
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

# ml model for gender detection
import newgender

# Load environment variables from a .env file
load_dotenv()

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to analyze sentiment of text and return compound score
def analyze_sentiment(text):
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score['compound']

# Get OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with the API key
client = OpenAI(api_key=api_key)

# Create Flask application
app = Flask(__name__)

# Determine the voice for text-to-speech based on gender
if newgender.essential() == 'Male':
    avaj = 'nova'
else:
    avaj = 'echo'

# Function to detect X-ray related terms in text and trigger a specific function
def xraybhai(text):
    regex_pattern = r"\b(X-ray|xray|scan|interpret|analysis|analyze|analysing|analyzing)(?:\s+\b(X-ray|xray|xrays|X-rays|scan|scans|interpret|interprets|analysis|analyze|analysing|analyzing)\b)+\b"
    if re.search(regex_pattern, text, flags=re.IGNORECASE):
        if not re.search(r"\b(no|don't|dont|do not|not|not at all)\s+\b(analysis|analyse|analysis|analyze|analysing|analyzing|interpretation|scan)\b", text, flags=re.IGNORECASE):
            from AI_Models.xray import xray
            return xray.xrayhello()
    return None

# Function to detect brain tumor related terms in text and trigger a specific function
def braintumor(text):
    regex_pattern = r"\b(MRI|scan|interpret|analysis)(?:\s+\b(MRI|scan|analyse|analysis|analyze|analysing|analyzing|interpret|scan|analysis)\b)+\b"
    if re.search(regex_pattern, text, flags=re.IGNORECASE):
        if not re.search(r"\b(no|don't|dont|do not|not|not at all)\s+\b(analysis|analyse|analysis|analyze|analysing|analyzing|interpretation|scan)\b", text, flags=re.IGNORECASE):
            from AI_Models.brain_tumor import brain_tumor
            return brain_tumor.brain_tumor1()
    return None

# Function to get response from OpenAI ChatGPT model
def send_message(message):
    if not isinstance(message, str):
        raise ValueError("Message must be a string")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chatbot also a counsellor, you have to console people when they are sad or depressed. also use most human like accent along with umm, uh so that it could sound more natural and human like"},
            {"role": "user", "content": message}
        ],
        max_tokens=100,
        temperature=0.7
    )
    return response.choices[0].message.content

# Function to check if the sentiment indicates depression
def send_message1(message):
    sentiment_score = analyze_sentiment(message)
    depression_flag = sentiment_score < -0.5
    return depression_flag

# Function to check if the sentiment indicates sadness
def send_message2(message):
    sentiment_score = analyze_sentiment(message)
    sadness_flag = sentiment_score < -0.2
    return sadness_flag

# Function to convert text to speech and save as an MP3 file
import time
def convert_to_speech(text):
    speech_file_path = "static/output.mp3"
    
    response = client.audio.speech.create(
        model="tts-1",
        voice=avaj,
        input=text
    )

    # Save the generated audio to a file
    response.stream_to_file(speech_file_path)

    # Return the URL to the saved audio file with a timestamp to avoid caching
    return f"/output.mp3?{int(time.time())}"

# Route to render the main index page
@app.route('/')
def index():
    return render_template('index.html')

# Main API route to handle transcription, analyze it, and respond with detections and audio URL
@app.route('/save-transcription', methods=['POST'])
def save_transcription():
    data = request.get_json()
    transcription = data['transcription']

    # Save the transcription to a file
    with open('transcription.txt', 'w') as f:
        f.write(transcription)   

    # Get chatbot response from OpenAI
    chat_response = send_message(transcription)
    
    # Check for depression and sadness in the transcription
    depressed_detector = send_message1(transcription)
    sad_detector = send_message2(transcription)
    
    # Check for X-ray and brain tumor related terms
    xray_detector = xraybhai(transcription)
    braintumor_detector = braintumor(transcription)
    
    # Convert chatbot response to speech and get the audio URL
    audio_url = convert_to_speech(chat_response)
    
    # Return the results as a JSON response
    # Now i used AJAX in JavaScript to connect the api, don't know about Rasberry PI
    return jsonify({'message': 'Transcription saved successfully', 'chat_response': chat_response, 'audio_url': audio_url, 'depressed_flag': depressed_detector, 'sad_detector': sad_detector, 'xray_detector': xray_detector, 'braintumor_detector': braintumor_detector})

# Route to serve the generated audio file
@app.route('/output.mp3')
def serve_audio():
    return send_from_directory('static', 'output.mp3')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5050)
