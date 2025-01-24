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

            file.seek(0, os.SEEK_END)  # Move to the end of the file
            file_size = file.tell()  # Get the current position (size of the file)
            file.seek(0)  # Reset the file pointer to the beginning

            print(f"File size: {file_size} bytes")
            if file_size > 15 * 1024 * 1024:  # Check if file size exceeds 15 MB
                return {"error": "File size exceeds 15 MB limit."}

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

@analyzer_blueprint.route('/api/analyze', methods=['POST'])
def analyze_midi_endpoint():
    result = []
    for file in request.files.values():
        result.append(analyze_file(file))
    return result, 200
