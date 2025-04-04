import os
import speech_recognition as sr
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai 
import re
import sqlite3

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("AIzaSyCGNMSoVt0oEpjypMu044KWJDaP1xC6Mwc")

# Initialize Gemini AI
genai.configure(api_key="AIzaSyCGNMSoVt0oEpjypMu044KWJDaP1xC6Mwc")
model = genai.GenerativeModel("gemini-1.5-pro-latest")  

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
    file_path = "input.wav"
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

    # AI prompt for evaluation
    prompt = f"""
    You are an AI debate coach. The topic of the debate is: "{topic}".

    **1️⃣ Evaluate the argument based on the following criteria:**  
    - **Logical Structure:** Is the argument well-organized? Does it follow a clear progression? If it's already structured well, state that no improvements are necessary.  
    - **Clarity & Coherence:** Is the argument clear and easy to understand? Are there ambiguous or vague points? If it's already clear, explicitly mention that.  
    - **Supporting Evidence:** Does the argument provide strong evidence? If it lacks evidence, suggest improvements. If it's well-supported, state that it's sufficient.  
    - **Potential Counterarguments:**  
      - Identify specific counterarguments that an opposing debater might use.  
      - Provide at least **one concrete example of a counterpoint** phrased as a debate challenge (e.g., “If we allow X, then what stops Y?”).  

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
    - **Potential Counterarguments:**  
      - (general explanation of weaknesses in counterarguments)  
      - **Example Counterpoint:** *"If we allow X, then what stops Y?"*  

    **Improved Argument:**  
    (Provide the improved version of the argument)
    """

    try:
        response = model.generate_content(prompt)

        # Handle blocked responses gracefully
        if not response.parts or not response.text:
            return jsonify({
                "error": "⚠️ AI could not generate a response due to content restrictions. Please rephrase your argument."
            }), 400

        ai_output = response.text.strip()

        # Extract rationality score
        score_line = next((line for line in ai_output.split("\n") if "Rationality Score:" in line), None)
        rationality_score = float(re.search(r"[-+]?\d*\.\d+|\d+", score_line).group()) if score_line else 0.5

        # Extract reason for score
        reason_start = ai_output.find("**Reasoning for Score:**")
        reason_for_score = ai_output[reason_start:].strip() if reason_start != -1 else "No reasoning provided."

        # Extract feedback
        feedback_start = ai_output.find("**Feedback:**")
        feedback = ai_output[feedback_start:].strip() if feedback_start != -1 else "No feedback provided."

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "rationality_score": rationality_score,
        "reason_for_score": reason_for_score,
        "feedback": feedback
    })

@app.route("/generate-motion", methods=["POST"])
def generate_motion():
    data = request.get_json()
    topic = data.get("topic", "General")

    prompt = f"Suggest a debate motion related to {topic}."
    response = model.generate_content(prompt)

    return jsonify({"motion": response.text.strip()})

@app.route("/save-argument", methods=["POST"])
def save_argument():
    """Saves an evaluated argument to the SQLite database."""
    data = request.get_json()
    if not data or "email" not in data or "topic" not in data or "argument" not in data or "score" not in data or "feedback" not in data:
        return jsonify({"error": "Missing data"}), 400  # Return 400 if any required field is missing.

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO arguments (email, topic, argument, score, feedback) 
            VALUES (?, ?, ?, ?, ?)
        """, (data["email"], data["topic"], data["argument"], data["score"], data["feedback"]))

        conn.commit()
        conn.close()
        
        return jsonify({"message": "Argument saved successfully!"}), 201  # Return 201 Created on success.
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 for any internal server error.

@app.route("/get-arguments", methods=["GET"])
def get_arguments():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email parameter is missing"}), 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic, argument, score, feedback FROM arguments WHERE email = ?", (email,))
    arguments = cursor.fetchall()
    conn.close()

    if not arguments:
        return jsonify({"message": "No saved arguments found."}), 404

    result = [
        {
            "id": row[0],  # ✅ Include the ID field
            "topic": row[1],
            "argument": row[2],
            "score": row[3],
            "feedback": row[4]
        } 
        for row in arguments
    ]
    return jsonify({"arguments": result}), 200

@app.route("/delete-argument", methods=["POST"])
def delete_argument():
    """Deletes an argument by ID."""
    data = request.get_json()
    argument_id = data.get("id")

    if not argument_id:
        return jsonify({"error": "Missing argument ID"}), 400  

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM arguments WHERE id=?", (argument_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Argument deleted successfully!"}), 200  

    except Exception as e:
        return jsonify({"error": str(e)}), 500  

@app.route("/get-leaderboard", methods=["GET"])
def get_leaderboard():
    """Returns the top users based on argument count and average score."""
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT email, COUNT(*) AS total_arguments, AVG(score) AS avg_score
            FROM arguments
            GROUP BY email
            ORDER BY avg_score DESC
            LIMIT 10
        """)
        leaderboard = cursor.fetchall()
        conn.close()

        # Convert to JSON format
        leaderboard_data = [
            {"email": row[0], "total_arguments": row[1], "average_score": round(row[2], 2) if row[2] else 0}
            for row in leaderboard
        ]

        return jsonify({"leaderboard": leaderboard_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
