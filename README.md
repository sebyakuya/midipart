# MIDIPART: MIDI Piano Assessment Rating Tool

This tool tries to rate a MIDI file to be played in a piano.

## What does it do?

It iterates over every MIDI file in a given directory and analyzes its internal structure to identify potential elements that could help to identify its difficulty.

Among the parameters used are:
* The key signature
* The time signature
* The number of notes
* The velocity of pressed keys
* The use of sustain pedal
* And many others

These parameters are then calibrated internally. The calibration is based on a weighted mean of all the parameters. Each parameter has it's own internal function to determine which value should return. 

The "difficulty" attribute that is exported within the Excel file that this application produces is a value between 0 and 1 that should help to identify if the song is easier or harder to play.

So, for example, if we only take into account the number of notes and the use of sustain pedal we could find the following case:

* Number of notes (weight=0.8): 1 if there are more than 10000 notes, otherwise 0
* Sustain pedal (weight=0.2): 1 if used, otherwise 0

Song with 12000 notes and sustain pedal: 0.8*1+0.2*1 = 1
Song with 8000 notes and sustain pedal: 0.8*0+0.2*1 = 0.2
Song with 100 notes and no sustain pedal: 0.8*0+0.2*0 = 0

*These are not real weights, it's just an example.

I'm no expert in music theory but this works more or less until more parameters are added and existing ones are refined to be more accurate.

## A note on Synthesia

Synthesia's settings folder (usually found in C:\Users\<user>\AppData\Roaming\Synthesia)) has a file called songInfo.xml.
This file contains information about songs, including the difficulty.
The Excel sheet produced by this application automatically generates the XML nodes to be copypasted into that file, so you can have this information directly into Synthesia.

Just copy the "synthesia" column into this file.


## How to use it

You will find a Windows executable inside the dist folder.

### From CMD or Powershell

    midipart.exe --folder x/y/z --output x/y/z

### Just using the executable

    midipart.exe
    # Will ask you to indicate folder and output paths.

### Using python

    cd midipart
    python midipart.py