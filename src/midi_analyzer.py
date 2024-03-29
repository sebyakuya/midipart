import hashlib
import os.path


class MidiAnalyzer:

    def __init__(self, midi):
        self.midi = midi
        self.parameters = self.get_statistics()
        self.values = dict()
        self.values["file"] = os.path.basename(midi.filename)
        self.values["abspath"] = midi.filename
        self.values["hash"] = self.calculate_md5()
        self.get_difficulty()
        self.values["synthesia"] = f"<SongInfo hash='{self.values['hash']}' version='1' difficulty='{str(self.values['difficulty']*100)}' />"

    def __str__(self):
        result = "",
        for k, v in self.values.items():
            result += f"{k}: {v}\n",
        return result

    def calculate_md5(self):
        with open(self.midi.filename, 'rb') as f:
            # Read the file in chunks to avoid loading the entire file into memory
            chunk_size = 1024
            md5_hash = hashlib.md5()
            while chunk := f.read(chunk_size):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()


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
            "time_signature": 0,
            "key_signature": 0,
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

    def get_time_signature(self):
        result = 0

        for msg in self.midi:
            if msg.type == "time_signature":
                if msg.numerator == 2 and msg.denominator == 4:
                    result = max(result, 0.2)
                elif msg.numerator == 3 and msg.denominator == 4:
                    result = max(result, 0.2)
                elif msg.numerator == 4 and msg.denominator == 4:
                    result = max(result, 0.2)
                elif msg.numerator == 6 and msg.denominator == 8:
                    result = max(result, 0.5)
                elif msg.numerator == 9 and msg.denominator == 8:
                    result = max(result, 0.5)
                elif msg.numerator == 12 and msg.denominator == 8:
                    result = max(result, 0.5)
                elif msg.numerator == 5 and msg.denominator == 4:
                    result = max(result, 0.8)
                elif msg.numerator == 7 and msg.denominator == 8:
                    result = max(result, 0.8)
                elif msg.numerator == 11 and msg.denominator == 8:
                    result = max(result, 0.8)
                else:
                    # Uncommon time signature
                    result = 1

        return result

    def get_key_signature(self):
        result = 0

        key_signatures = {
            "Em": 0.1,
            "E": 0.2,
            "C": 0.3,
            "Gm": 0.4,
            "Dm": 0.5,
            "F": 0.6,
            "D": 0.7,
            "Cm": 0.8,
            "F#": 0.9,
            "Bb": 0.35,
            "Eb": 0.45,
            "Ab": 0.55,
            "Db": 0.65,
            "Gb": 0.75,
            "Cb": 0.85,
            "G": 0.9
        }

        for msg in self.midi:
            if msg.type == "key_signature":

                try:
                    result = key_signatures[msg.key]
                except KeyError:
                    result = 1

                break

        return result

    def get_velocity(self):
        """How keys are pressed is something that can increase the difficulty of a piece"""
        result = 0

        velocity = set()
        for msg in self.midi:
            if msg.type == "note_on":
                velocity.add(msg.velocity)

        diff = len(velocity)
        self.values["velocity"] = diff

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
        self.values["duration"] = round(total, 2)

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
                "value": self.get_time_signature()
            },
            {
                "weight": 1,
                "value": self.get_key_signature()
            },
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
