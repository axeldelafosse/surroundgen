# Surroundgen

Surroundgen is a surround and immersive spatial audio toolkit. It helps you separate and generate multichannel audio files.

## Installation

`python3 -m pip install surroundgen`

## Separation

Input: a multichannel audio file
Output: a directory with a mono file for each channel

`surroundsep "Kraftwerk - Mitternacht.flac"`

## Generation

Input: a directory with a mono file for each channel (following a naming convention)
Output: a multichannel audio file (in the same directory)

`surroundgen "Kraftwerk - Mitternacht"`
