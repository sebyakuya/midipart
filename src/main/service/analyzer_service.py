from flask import jsonify

from src.main.aux_functions.midi_functions import get_midi_api, get_midi
from src.main.model.midi_analyzer import MidiAnalyzer


def test():
    return jsonify({"message": "Hello from Flask!"})


def analyze_midi(midi_file):
    midi = get_midi(midi_file)
    mclass = MidiAnalyzer(midi)
    values = mclass.get_values()
    return values


