import argparse
import os

import pandas as pd
from rich.progress import Progress
from rich.prompt import Prompt
from rich import print
from midipart.src.midi_analyzer import MidiAnalyzer
from midipart.src.midi_functions import get_midi_files_in_folder, get_midi

parser = argparse.ArgumentParser(
    prog='MIDIPART',
    description='MIDI Piano Assistant Rating Tool',
    epilog='A tool to rate the difficulty of MIDI files')
parser.add_argument('--folder', type=str, help='Text to be printed')
parser.add_argument('--output', type=str, help='Text to be printed')


def report(folder, output):

    midi_files = get_midi_files_in_folder(folder)

    df = pd.DataFrame(
        columns=["file", "notes", "min_note", "max_note", "diff_note", "velocity", "sustain", "channels", "duration",
                 "difficulty",
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


def delete(folder):

    midi_files = get_midi_files_in_folder(folder)

    print(f"Found {len(midi_files)} MIDI files")

    hashes = set()
    to_delete = set()
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
    args = parser.parse_args()

    print("##########################################")
    print("MIDIPART: MIDI Piano Assistant Rating Tool")
    print("##########################################")
    if not args.folder:
        print("No songs folder provided. Ensure that you indicated a valid path. "
              "E.g. [green]midipart --folder /path/to/midi")
        exit(-1)

    print("Available actions:")
    print("[red]1.[/red] Report: creates an Excel spreadsheet with the information from MIDI files")
    print("[red]2.[/red] Delete: removes MIDI files that are duplicated")
    action = Prompt.ask("What to do? Select number and press Enter", choices=["1", "2"])

    if action == "1":
        if not args.output:
            print("No output path provided. Ensure that you indicated a valid path. "
                  "E.g. [green]midipart --folder /path/to/midi --output /path/to/export/result")
            exit(-1)
        report(args.folder, args.output)
    elif action == "2":
        delete(args.folder)
    else:
        print("Invalid option")

