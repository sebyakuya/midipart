import hashlib
import os.path


class MidiAnalyzer:

    def __init__(self, midi):
        self.midi = midi
        self.parameters = self.get_statistics()
        self.values = dict()
        self.values["file"] = os.path.basename(midi.filename)
        self.values["abspath"] = midi.filename
        self.values["hash"] = self.sha256_hash_file()
        self.get_difficulty()

    def __str__(self):
        result = "",
        for k, v in self.values.items():
            result += f"{k}: {v}\n",
        return result

    def sha256_hash_file(self):
        sha256_hash = hashlib.sha256()

        with open(self.midi.filename, "rb") as file:
            # Read the file in chunks to handle large files
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    def get_values(self):
        return self.values

    def get_statistics(self):
        midi_parameters = {
            "note_off": 0,
            "note_on": 0,
            "polytouch": 0,
            "control_change": 0,
            "program_change": 0,
            "aftertouch": 0,
            "pitchwheel": 0,
            "sysex": 0,
            "quarter_frame": 0,
            "songpos": 0,
            "song_select": 0,
            "tune_request": 0,
            "clock": 0,
            "start": 0,
            "continue": 0,
            "stop": 0,
            "active_sensing": 0,
            "reset": 0,
        }
        for msg in self.midi:
            if msg.type not in midi_parameters:
                midi_parameters[msg.type] = 0
            midi_parameters[msg.type] += 1

        return midi_parameters

    # Control change control=64 es el sustain, es el uso del pedal

    # El channel parece indicar el "instrumento", se podria hacer algo para poner un canal 2 para la mano izquierda
    # para todas las teclas por debajo de una en concreto
    # Cantidad de notas
    # Variabilidad en la forma de presionar las notas (velocity)
    # Numero de instrumentos (realmente esto solo indica si la cancion es tocable o no)
    # Distancia entre la nota mas baja y la mas alta
    # Acordes (esto es muy subjetivo, pero podemos decir que los acordes de teclas blancas son mas faciles)
    # El problema de esto es detectar un acorde entre todas las notas
    # Uso del sustain
    # Compas
    # Armadura

    def get_velocity(self):
        """How keys are pressed is something that can increase the difficulty of a piece"""
        result = 0

        velocity = set()
        for msg in self.midi:
            if msg.type == "note_on":
                velocity.add(msg.velocity)

        diff = len(velocity)

        if diff > 100:
            result = 1
        elif 50 < diff <= 100:
            result = 0.5
        elif 10 < diff <= 50:
            result = 0.3
        elif diff < 10:
            result = 0.1
        return result

    def get_number_of_notes(self):
        """A song with many notes will be harder than one with less notes, generally"""
        result = 0
        if self.parameters["note_on"] > 3000:
            result = 1
        elif 1500 <= self.parameters["note_on"] <= 3000:
            result = 0.5
        elif self.parameters["note_on"] < 1500:
            result = 0
        self.values["notes"] = self.parameters["note_on"]
        return result

    def get_min_max_tones(self):
        """The wider the range between keys the harder to play"""
        min_note = -1
        max_note = -1
        diff_note = -1

        if self.parameters["note_on"] != 0:
            for msg in self.midi:
                if msg.type == "note_on":
                    if min_note == -1:
                        min_note = msg.note
                    if max_note == -1:
                        max_note = msg.note
                    min_note = min(min_note, msg.note)
                    max_note = max(max_note, msg.note)

            if min_note < 20:
                min_note = 20
            if max_note > 108:
                max_note = 108

            min_note = min_note - 20
            max_note = max_note - 20

            diff_note = max_note - min_note
            if diff_note > 88:
                diff_note = -1

        result = 0
        if diff_note < 5:
            result = 0
        elif 5 <= diff_note <= 30:
            result = 0.5
        elif diff_note > 30:
            result = 1

        self.values["min_note"] = min_note
        self.values["max_note"] = max_note
        self.values["diff_note"] = diff_note

        return result

    def get_sustain_use(self):
        """Use of sustain pedal is an advanced technique"""
        sustain = 0
        for msg in self.midi:
            if msg.type == "control_change":
                if msg.control == 64 and msg.value >= 64:
                    sustain += 1

        self.values["sustain"] = sustain

        result = 0
        if sustain > 0:
            result = 1

        return result

    def get_number_of_channels(self):
        """Many channels means that it will be difficult to make it sound like the original"""
        channels = set()
        for msg in self.midi:
            if msg.type == "note_on":
                channels.add(msg.channel)

        number_of_channels = len(channels)
        self.values["channels"] = number_of_channels

        result = 0
        if number_of_channels == 1:
            result = 0
        elif number_of_channels == 2:
            result = 0.5
        elif number_of_channels > 2:
            result = 1
        return result

    def get_time_in_seconds(self):
        """The longer the song, the harder to learn"""
        total = 0
        for msg in self.midi:
            try:
                total += msg.time
            except:
                pass
        self.values["duration"] = total

        result = 0
        if total > 600:
            result = 1
        elif 400 < total <= 600:
            result = 0.7
        elif 200 < total <= 400:
            result = 0.4
        elif 100 <= total <= 200:
            result = 0.2
        elif total < 100:
            result = 0.1

        return result

    def get_difficulty(self):
        parameters = [
            {
                "weight": 1,
                "value": self.get_velocity()
            },
            {
                "weight": 1,
                "value": self.get_number_of_notes()
            },
            {
                "weight": 1,
                "value": self.get_min_max_tones()
            },
            {
                "weight": 1,
                "value": self.get_sustain_use()
            },
            {
                "weight": 1,
                "value": self.get_number_of_channels()
            },
            {
                "weight": 1,
                "value": self.get_time_in_seconds()
            }
        ]

        # Weighted sum of parameters
        num = sum([x["weight"] * x["value"] for x in parameters])
        den = sum([x["weight"] for x in parameters])
        result = round(num / den, 2)

        self.values["difficulty"] = result

        return result
