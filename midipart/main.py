import os

import pandas as pd
import typer as typer
from rich.progress import Progress

from midipart.src.midi_analyzer import MidiAnalyzer
from midipart.src.midi_functions import get_midi_files_in_folder, get_midi

app = typer.Typer(no_args_is_help=True, add_completion=False, add_help_option=False)


@app.callback()
def callback():
    """MIDIPART: MIDI Piano Assessment Rating Tool"""


@app.command()
def report(folder: str = "", output: str = ""):
    if folder == "" or output == "":
        print("Run the following command: midipart report --folder /path/to/songs --output /path/to/store/report.xlsx")
        exit(-1)

    midi_files = get_midi_files_in_folder(folder)

    df = pd.DataFrame(
        columns=["file", "notes", "min_note", "max_note", "diff_note", "sustain", "channels", "duration", "difficulty",
                 "hash", "abspath"])

    print(f"Found {len(midi_files)} MIDI files")

    with Progress() as progress:
        task1 = progress.add_task("[red]Processing...", total=len(midi_files))

        for midi_file in midi_files:
            midi = get_midi(midi_file)
            if midi != "":
                mclass = MidiAnalyzer(midi)
                values = mclass.get_values()
                # print(values)
                df.loc[len(df.index)] = values
            progress.update(task1, advance=1)

    df.to_excel(os.path.join(output, "midipart.xlsx"))


@app.command()
def delete(folder: str = ""):
    if folder == "":
        print("Run the following command: midipart delete --folder /path/to/songs")
        exit(-1)

    midi_files = get_midi_files_in_folder(folder)

    print(f"Found {len(midi_files)} MIDI files")

    hashes = set()
    to_delete  = set()
    with Progress() as progress:
        task1 = progress.add_task("[red]Processing...", total=len(midi_files))

        for midi_file in midi_files:
            midi = get_midi(midi_file)
            if midi != "":
                mclass = MidiAnalyzer(midi)
                values = mclass.get_values()
                if values["hash"] not in hashes:
                    hashes.add(values["hash"])
                else:
                    print(f"Duplicated: {midi_file}")
                    to_delete.add(midi_file)

            progress.update(task1, advance=1)

    x = input("Delete? y/n")
    if x == "y":
        for midi_file in to_delete:
            print(f"Removing {midi_file}")
            os.remove(midi_file)


if __name__ == "__main__":
    app()
