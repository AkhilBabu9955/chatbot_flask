from flask import Flask, request, jsonify, render_template
import json
import textdistance

app = Flask(__name__)

# Load disease data
disease_data = json.loads(open('C:\\Users\\akhil\\OneDrive\\Documents\\flask_projects\\chatbot_flask\\disease_data_extended .json').read())

# List of disease names
disease_list = [d["name"] for d in disease_data["diseases"]]

# Store user session data
user_sessions = {}

# Function to get disease details
def get_disease_info(disease_name):
    for disease in disease_data["diseases"]:
        if disease['name'].lower() == disease_name:
            return {
                "Symptoms": disease['symptoms'],
                "Description": disease['description'],
                "Medicines": disease['medicines'],
                "Precautions": disease['precautions']
            }
    return None

# Function to correct spelling
def correct_spelling(user_input):
    return max(disease_list, key=lambda d: textdistance.JaroWinkler().similarity(user_input, d))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip().lower()
    session_id = data.get("session_id", "default")

    if session_id not in user_sessions:
        user_sessions[session_id] = {}

    if user_input in ["exit", "quit"]:
        return jsonify({"response": "Exiting chatbot. Goodbye!"})

    # If user says "yes", show medicines & precautions
    if user_input == "yes" and "current_disease" in user_sessions[session_id]:
        disease_info = get_disease_info(user_sessions[session_id]["current_disease"])
        if disease_info:
            response = (
                "<div class='message bot'><strong style='font-size: 18px;'>Here are the medicines and precautions:</strong></div>"
                f"<div class='message bot'><strong style='font-size: 16px;'>Medicines:</strong><br>{', '.join(disease_info['Medicines'])}</div>"
                f"<div class='message bot'><strong style='font-size: 16px;'>Precautions:</strong><br>{', '.join(disease_info['Precautions'])}</div>"
            )
        else:
            response = "<div class='message bot'>Sorry, I couldn't find that information.</div>"
        return jsonify({"response": response})

    # If user says "no", ask for another disease
    if user_input == "no":
        user_sessions[session_id].pop("current_disease", None)
        return jsonify({"response": "<div class='message bot'>Okay! You can enter another disease name.</div>"})

    corrected_disease = correct_spelling(user_input)
    disease_info = get_disease_info(corrected_disease.lower())

    if disease_info:
        user_sessions[session_id]["current_disease"] = corrected_disease.lower()
        response = (
            f"<div class='message bot'><strong style='font-size: 18px;'>Did you mean: {corrected_disease}?</strong></div>"
            f"<div class='message bot'><strong style='font-size: 16px;'>Symptoms:</strong><br>{', '.join(disease_info['Symptoms'])}</div>"
            f"<div class='message bot'><strong style='font-size: 16px;'>Description:</strong><br>{disease_info['Description']}</div>" 

           "<div class='message bot'><br><strong style='font-size: 16px;'>Would you like me to suggest medicines and precautions? (yes/no)</strong></div>"
        )
    else:
        response = "<div class='message bot'>Disease not found. Please enter a valid disease name.</div>"

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
