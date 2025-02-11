import os
import threading
import speech_recognition as sr
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai  # Google Gemini API

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")  # Use Gemini-Pro for text-based tasks

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Welcome to the AI Debate Coach Backend 🎤</h1>"

@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    """Converts speech to text using Google Speech Recognition."""
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

@app.route("/evaluate-argument", methods=["POST"])
def evaluate_argument():
    """Uses AI to analyze and provide feedback on the argument and generate an improved version."""
    data = request.get_json()
    if not data or "text" not in data or "topic" not in data:
        return jsonify({"error": "No text or topic provided"}), 400
    
    topic = data["topic"]
    argument = data["text"]

    # AI model prompt using both topic and argument
    prompt = f"""
    You are an AI debate coach. The topic of the debate is: "{topic}".

    1️⃣ **Evaluate the following argument** in the context of this topic. Provide feedback on:
       - Logical structure
       - Clarity and coherence
       - Supporting evidence
       - Potential counterarguments

    2️⃣ **Then, generate an improved version** of the argument that:
       - Fixes the weaknesses
       - Strengthens logical reasoning
       - Uses better evidence or examples
       - Is more persuasive and structured

    **User's Argument:**  
    {argument}

    **Format your response as follows:**  
    ---
    **Feedback:**  
    - Bullet points listing improvements  

    **Improved Argument:**  
    - Provide the enhanced version of the argument  
    """

    try:
        response = model.generate_content(prompt)
        ai_output = response.text.strip()  # Extract the generated text
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging
        return jsonify({"error": str(e)}), 500

    return jsonify({"feedback": ai_output})

# Function to start Streamlit frontend
def run_streamlit():
    os.system("streamlit run frontend.py --server.port=8501 --server.headless true")

if __name__ == "__main__":
    threading.Thread(target=run_streamlit, daemon=True).start()
    app.run(debug=True)
