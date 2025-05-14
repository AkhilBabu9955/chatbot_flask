from flask import Flask, request, jsonify, render_template
import json
import pickle
import spacy
import textdistance
from keras.models import load_model

app = Flask(__name__)

# Load spaCy's English model
nlp = spacy.load('en_core_web_sm')

# Common path for files
# BASE_PATH = "C:\\Users\\akhil\\OneDrive\\Documents\\flask_projects\\chatbot_flask\\"

# Load necessary files
MODEL_PATH = "C:\\Users\\akhil\\OneDrive\\Documents\\flask_projects\\chatbot_flask\\disease_prediction_model.h5"
WORDS_PATH = "C:\\Users\\akhil\\OneDrive\\Documents\\flask_projects\\chatbot_flask\\words.pkl"
CLASSES_PATH = "C:\\Users\\akhil\\OneDrive\\Documents\\flask_projects\\chatbot_flask\\classes.pkl"
DATA_PATH ="C:\\Users\\akhil\\OneDrive\\Documents\\flask_projects\\chatbot_flask\\disease_data_extended .json"

words = pickle.load(open(WORDS_PATH, 'rb'))
classes = pickle.load(open(CLASSES_PATH, 'rb'))
model = load_model(MODEL_PATH)

# Load disease data
try:
    with open(DATA_PATH, 'r', encoding="utf-8") as f:
        disease_data = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"File not found: {DATA_PATH}")

# Create a disease list for spell correction
disease_list = [d['name'].lower() for d in disease_data["diseases"]]

def get_disease_info(disease_name):
    """Retrieve disease details"""
    for disease in disease_data["diseases"]:
        if disease['name'].lower() == disease_name:
            return {
                "Symptoms": disease['symptoms'],
                "Description": disease['description'],
                "Medicines": disease['medicines'],
                "Precautions": disease['precautions']
            }
    return None

def correct_spelling(user_input):
    """Correct spelling using Jaro-Winkler similarity"""
    corrected_name = max(disease_list, key=lambda d: textdistance.JaroWinkler().similarity(user_input, d))
    return corrected_name

@app.route('/')
def home():
    return render_template('index9.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handles user queries and follows the correct flow"""
    data = request.get_json()
    user_input = data.get("message", "").strip().lower()

    if not user_input:
        return jsonify({"response": "Please enter a valid disease name."})

    if user_input in ["yes", "no"]:
        prev_disease = data.get("prev_disease")
        if not prev_disease:
            return jsonify({"response": "Please enter a disease name first."})

        disease_info = get_disease_info(prev_disease)
        if not disease_info:
            return jsonify({"response": "Disease information not found."})

        if user_input == "yes":
            medicines = "<b>Medicines:</b> " + ", ".join(disease_info["Medicines"])
            precautions = "<b>Precautions:</b> " + ", ".join(disease_info["Precautions"])
            return jsonify({"response": f"Here are the medicines and precautions.<br>{medicines}<br>{precautions}"})

        return jsonify({"response": "Okay! You can enter another disease name."})

    # Correct spelling if needed
    corrected_disease = correct_spelling(user_input)

    if corrected_disease != user_input:
        return jsonify({
            "response": f"Did you mean: <b>{corrected_disease}</b>?",
            "corrected_disease": corrected_disease
        })

    disease_info = get_disease_info(corrected_disease)

    if not disease_info:
        return jsonify({"response": "Disease not found. Please enter a valid disease name."})

    symptoms = "<b>Symptoms:</b> " + ", ".join(disease_info["Symptoms"])
    description = "<b>Description:</b> " + disease_info["Description"]

    return jsonify({
        "corrected_disease": corrected_disease,
        "response": f"{symptoms}<br>{description}",
        "follow_up": "Would you like me to suggest medicines and precautions? (yes/no)",
        "prev_disease": corrected_disease
    })

if __name__ == '__main__':
    app.run(debug=True)
