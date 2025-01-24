from src.main.aux_functions.midi_functions import get_midi
from src.main.model.midi_analyzer import MidiAnalyzer


def test():
    return {"message": "Hello!"}


def analyze_midi(midi_file):
    try:
        print(f"Starting analysis of {midi_file}")
        midi = get_midi(midi_file)
        mclass = MidiAnalyzer(midi)
        values = mclass.get_values()
        return values
    except Exception as e:
        return {"error": f"MIDI file couldn't be analyzed. The file may be corrupted or is not a valid MIDI file"}



