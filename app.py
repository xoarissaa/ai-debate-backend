import os
import threading
import speech_recognition as sr
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Welcome to the AI Debate Coach Backend 🎤</h1>"

@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    audio_file = request.files["file"]
    file_path = os.path.join("speech_samples", "input.wav")
    audio_file.save(file_path)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return jsonify({"transcription": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech Recognition API unavailable"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Function to start Streamlit
def run_streamlit():
    os.system("streamlit run frontend.py --server.port=8501 --server.headless true")

if __name__ == "__main__":
    threading.Thread(target=run_streamlit, daemon=True).start()
    app.run(debug=True)
