# Surroundgen

Surroundgen is a surround and immersive spatial audio toolkit. It helps you separate and generate multichannel audio files.

## Installation

`python3 -m pip install surroundgen`

## Separation

Input: a multichannel audio file

Output: a directory with a mono file for each channel

`surroundsep "Kraftwerk - Mitternacht.flac"`

### ORTF 3D

ORTF 3D recordings use eight discrete channels in this order:

1. `L` — lower left/front
2. `R` — lower right/front
3. `LS` — lower left surround/rear
4. `RS` — lower right surround/rear
5. `Lh` — left height/top front (`LTF`)
6. `Rh` — right height/top front (`RTF`)
7. `LSh` — left surround height/top rear (`LTR`)
8. `RSh` — right surround height/top rear (`RTR`)

This mapping follows the [SCHOEPS ORTF-3D setup guide](https://schoeps.de/fileadmin/user_upload/user_upload/Downloads/Bedienungsanleitungen/SCHOEPS_ORTF-3D_Windshield_Setup_Guide_02.pdf)
and [technical paper](https://schoeps.de/fileadmin/user_upload/user_upload/Downloads/Vortraege_Aufsaetze/Papers/ORTF3DArticle060916_1473169351.pdf).

`surroundsep` automatically recognizes filenames containing `ORTF3D` or the channel
signature `L,R,Ls,Rs,Lh,Rh,Lsh,Rsh`. For a renamed file without either marker,
specify the layout explicitly:

`surroundsep --layout ortf-3d "recording.wav"`

ORTF 3D is split by channel index and is never rematrixed as conventional 7.1.

## Generation

Input: a directory with a mono file for each channel (following a naming convention)

Output: a multichannel audio file (in the same directory)

`surroundgen "Kraftwerk - Mitternacht"`
