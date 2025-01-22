import os

from flask import Blueprint, jsonify, request

from src.main.service.analyzer_service import test, analyze_midi

analyzer_blueprint = Blueprint('analyzer', __name__)

@analyzer_blueprint.route('/api', methods=['GET'])
def home():
    return test()

# Additional endpoints can be added here
@analyzer_blueprint.route('/api/analyze', methods=['POST'])
def analyze_midi_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    filename = file.filename
    if filename == '':
        return jsonify({"error": "No selected file"}), 400
    else:
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in [".mid", ".MID"]:
            return jsonify({"error": "File format not supported. Please upload a .mid file."}), 400
        else:
            file.save(os.path.join("files", filename))
            result = analyze_midi(os.path.join("files", filename))  # Assuming analyze_midi can handle the file object
            return jsonify(result)


   
