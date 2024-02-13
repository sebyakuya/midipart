import os

from mido import MidiFile


def get_midi_files_in_folder(folder):
    midi_files = []
    print(folder)
    for folder, _, files in os.walk(folder):
        for file in files:
            p = os.path.join(folder, file)
            if is_midi_file(p):
                midi_files.append(p)

    return midi_files


def is_midi_file(file_path):
    try:
        with open(file_path, "rb") as file:
            header = file.read(4)
            if header == b"MThd" or header == b"RIFF":  # MIDI files start with the header "MThd" or "RIFF"
                return True
    except IOError:
        pass
    return False


def get_midi(path):
    try:
        midi = MidiFile(path)
    except OSError:
        print(f"Error reading {path}")
        midi = ""
    except Exception:
        print(f"Error reading {path}")
        midi = ""
    return midi


def play_midi(midi):
    for msg in midi.play():
        if msg.type == "note_on" and msg.channel == 1:
            # playsound(audio_notes[str(msg.note - 20)], block=False)
            pass
