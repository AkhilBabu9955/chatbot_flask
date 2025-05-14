from flask import Flask, render_template, request, jsonify
import json
import pickle
import numpy as np
from tensorflow.keras.models import load_model

# Load necessary files
disease_classes = pickle.load(open("classes.pkl", "rb"))
word_index = pickle.load(open("words.pkl", "rb"))
model = load_model("disease_prediction_model.h5")

# Load disease information
disease_data = json.load(open("C:\\Users\\akhil\\OneDrive\\Documents\\flask_projects\\chatbot_flask\\data.json", encoding="utf-8"))

def get_disease_details(disease_name):
    """Retrieve disease details from JSON."""
    return disease_data.get(disease_name, None)

def suggest_disease(input_disease):
    """Suggests the closest matching disease name."""
    for disease in disease_classes:
        if input_disease.lower() in disease.lower():
            return disease
    return None

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_disease', methods=['POST'])
def get_disease():
    data = request.json
    disease_name = data.get("disease_name").strip()
    
    details = get_disease_details(disease_name)
    if details:
        response = {
            "status": "found",
            "disease": disease_name,
            "symptoms": details["symptoms"],
            "description": details["description"]
        }
    else:
        suggested = suggest_disease(disease_name)
        if suggested:
            response = {"status": "suggest", "suggested_disease": suggested}
        else:
            response = {"status": "not_found"}
    
    return jsonify(response)

@app.route('/get_treatment', methods=['POST'])
def get_treatment():
    data = request.json
    disease_name = data.get("disease_name").strip()
    details = get_disease_details(disease_name)
    
    if details:
        response = {
            "medicines": details["medicines"],
            "precautions": details["precautions"]
        }
        return jsonify(response)
    return jsonify({"error": "Disease details not found."})

if __name__ == '__main__':
    app.run(debug=True)
