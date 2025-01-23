import os

from flask import Blueprint, request

from src.main.aux_functions.midi_functions import is_midi_file
from src.main.service.analyzer_service import test, analyze_midi

analyzer_blueprint = Blueprint('analyzer', __name__)

def analyze_file(file):
    filename = file.filename
    if filename == '':
        return {"error": "No selected file"}
    else:
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in [".mid", ".MID"]:
            return {"error": "File format not supported. Please upload a .mid file."}
        else:
            file_path = os.path.join("files", filename)
            file.save(file_path)
            if not is_midi_file(file_path):
                return {"error": "File is not a MIDI file. Please upload a valid .mid file."}
            else:
                result = analyze_midi(file_path)
                os.remove(file_path)
                return result

@analyzer_blueprint.route('/api', methods=['GET'])
def home():
    return test()

# Additional endpoints can be added here
@analyzer_blueprint.route('/api/analyze', methods=['POST'])
def analyze_midi_endpoint():
    if 'file' not in request.files:
        return {"error": "No file part"}, 400

    file = request.files['file']
    result = analyze_file(file)

    if "error" not in result:
        return result, 200
    else:
        return result, 400

@analyzer_blueprint.route('/api/analyzem', methods=['POST'])
def analyze_midi_endpoint_multi():
    result = []
    for file in request.files.values():
        result.append(analyze_file(file))
    return result, 200
