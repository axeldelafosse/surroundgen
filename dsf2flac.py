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


def convert():
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            INPUT_PATH,
            "-c:a",
            "flac",
            "-ar",
            "48000",
            f"{FILE_NAME}.flac",
        ]
    )


def main():
    global BASE_PATH, FILE_EXTENSION
    BASE_PATH = os.path.basename(INPUT_PATH)
    FILE_EXTENSION = os.path.splitext(BASE_PATH)[1]

    global FILE_NAME, INPUT_DIR, FILE_PATH
    FILE_NAME = strip_accents(BASE_PATH.removesuffix(FILE_EXTENSION))

    convert()


if __name__ == "__main__":
    main()
