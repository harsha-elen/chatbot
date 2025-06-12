from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file.")

# Configure Gemini
genai.configure(api_key=api_key)

# Updated system instruction to enforce domain restriction
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "You are a helpful assistant for farmers. Only respond to agriculture-related "
        "questions. If someone asks about topics unrelated to farming—like movies, politics, "
        "or general knowledge—politely refuse to answer."
    )
)

chat = model.start_chat(history=[])

# Initialize Flask app
app = Flask(__name__)

# Farming keyword filter
FARMING_KEYWORDS = [
    "crop", "pest", "soil", "fertilizer", "irrigation", "weather", "climate",
    "plant", "yield", "agriculture", "farming", "harvest", "rainfall", "monsoon",
    "seed", "insect", "weeds", "farm", "disease", "season", "summer", "winter"
]

def is_farming_question(text):
    return any(keyword in text.lower() for keyword in FARMING_KEYWORDS)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "").strip()

    if not is_farming_question(question):
        return jsonify({
            "response": "Sorry, I can only help with farming-related questions. Please ask about crops, soil, pests, weather, or agriculture."
        })

    try:
        response = chat.send_message(question, stream=True)
        answer = "".join(chunk.text for chunk in response if chunk.text)
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
