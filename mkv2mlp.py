#!/usr/bin/env python3

import argparse
import subprocess
import os
from pathlib import Path
import unicodedata

INSTALL_DIR = Path(__file__).parent.absolute()
PROCESS_DIR = os.getcwd()

parser = argparse.ArgumentParser()

parser.add_argument(
    dest="POSITIONAL_INPUT_PATH", nargs="?", help="the path to the input file"
)
parser.add_argument(
    "-i", "--input", dest="INPUT_PATH", help="the path to the input file"
)
parser.add_argument(
    "-o",
    "--output",
    dest="OUTPUT_PATH",
    default="output"
    if str(INSTALL_DIR) == PROCESS_DIR or INSTALL_DIR.as_posix() == PROCESS_DIR
    else ".",
    help="the path to the output folder",
)
args = parser.parse_args()

INPUT_PATH = args.POSITIONAL_INPUT_PATH or args.INPUT_PATH
OUTPUT_PATH = (
    args.OUTPUT_PATH
    if os.path.isabs(args.OUTPUT_PATH)
    else os.path.join(PROCESS_DIR, args.OUTPUT_PATH)
)

def strip_accents(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    return str(text)

def get_truehd_track_number():
    print("Finding TrueHD track...")
    
    # Use mkvmerge to identify TrueHD track
    output = subprocess.check_output(
        ["mkvmerge", "-i", INPUT_PATH],
        universal_newlines=True
    )
    
    # Look for TrueHD track in the output
    for line in output.splitlines():
        if "TrueHD" in line:
            track_num = line.split(':')[0].split(' ')[-1]
            print(f"Found TrueHD track: {track_num}")
            return track_num
            
    raise ValueError("No TrueHD track found in the input file")

def extract_mlp():
    track_number = get_truehd_track_number()
    output_file = f"{FILE_NAME}.mlp"
    
    print(f"Extracting to {output_file}...")
    subprocess.run([
        "mkvextract",
        INPUT_PATH,
        "tracks",
        f"{track_number}:{output_file}"
    ])
    print("Done.")

def main():
    if not INPUT_PATH:
        parser.error("Input file is required")

    global BASE_PATH, FILE_EXTENSION
    BASE_PATH = os.path.basename(INPUT_PATH)
    FILE_EXTENSION = os.path.splitext(BASE_PATH)[1]

    global FILE_NAME
    FILE_NAME = strip_accents(BASE_PATH.removesuffix(FILE_EXTENSION))

    extract_mlp()

if __name__ == "__main__":
    main()
