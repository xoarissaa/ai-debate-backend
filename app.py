import os
import threading
import speech_recognition as sr
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai  # Google Gemini API
import re

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
    """Uses AI to analyze rationality, provide feedback, and improve the argument."""
    data = request.get_json()
    if not data or "text" not in data or "topic" not in data:
        return jsonify({"error": "No text or topic provided"}), 400
    
    topic = data["topic"]
    argument = data["text"]

    # Updated AI model prompt ensuring it always provides feedback on key areas
    prompt = f"""
    You are an AI debate coach. The topic of the debate is: "{topic}".

    **1️⃣ Evaluate the argument based on the following criteria:**  
    - **Logical Structure:** Is the argument well-organized? Does it follow a clear progression? If it's already structured well, state that no improvements are necessary.  
    - **Clarity & Coherence:** Is the argument clear and easy to understand? Are there ambiguous or vague points? If it's already clear, explicitly mention that.  
    - **Supporting Evidence:** Does the argument provide strong evidence? If it lacks evidence, suggest improvements. If it's well-supported, state that it's sufficient.  
    - **Potential Counterarguments:** Does the argument address opposing views? If not, suggest how it could improve. If it does, acknowledge that it is well-handled.  

    **2️⃣ Assess the rationality of the argument:**  
    - Provide a **rationality score** from **0 (highly emotional) to 1 (highly rational)**.  
    - Explain why the argument was scored that way.  

    **3️⃣ Generate an improved version of the argument** that:  
    - Incorporates the feedback above.  
    - Fixes weaknesses while keeping the argument’s core ideas.  
    - Uses better structure, clarity, and stronger reasoning if necessary.  

    **User's Argument:**  
    {argument}

    **Format your response as follows:**  
    ---
    **Rationality Score:** X.X  
    **Reasoning for Score:** (explanation)  

    **Feedback:**  
    - **Logical Structure:** (comment)  
    - **Clarity & Coherence:** (comment)  
    - **Supporting Evidence:** (comment)  
    - **Potential Counterarguments:** (comment)  

    **Improved Argument:**  
    (Provide the improved version of the argument incorporating feedback)
    """

    try:
        response = model.generate_content(prompt)

        # **Handle blocked responses gracefully**
        if not response.parts or not response.text:
            return jsonify({
                "error": "⚠️ AI could not generate a response due to content restrictions. Please rephrase your argument."
            }), 400

        ai_output = response.text.strip()  # Extract the generated text

        # Extract rationality score
        score_line = next((line for line in ai_output.split("\n") if "Rationality Score:" in line), None)

        if score_line:
            score_match = re.search(r"[-+]?\d*\.\d+|\d+", score_line)  # Extracts numeric value
            if score_match:
                rationality_score = float(score_match.group())
            else:
                rationality_score = 0.5  # Default if score not found
        else:
            rationality_score = 0.5  # Default if missing

        # Extract reason for score
        reason_start = ai_output.find("**Reasoning for Score:**")
        reason_for_score = "No explanation provided."
        if reason_start != -1:
            reason_end = ai_output.find("\n\n", reason_start)
            reason_for_score = ai_output[reason_start + len("**Reasoning for Score:**"):reason_end].strip()

        # Extract feedback (removes rationality score & reason)
        feedback_start = ai_output.find("**Feedback:**")
        feedback = ai_output[feedback_start:].strip() if feedback_start != -1 else "No feedback provided."

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "rationality_score": rationality_score,
        "reason_for_score": reason_for_score,
        "feedback": feedback
    })

# Function to start Streamlit frontend
def run_streamlit():
    os.system("streamlit run frontend.py --server.port=8501 --server.headless true")

if __name__ == "__main__":
    threading.Thread(target=run_streamlit, daemon=True).start()
    app.run(debug=True)
