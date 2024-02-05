#!/usr/bin/env python3

import argparse
import re
import subprocess
import os
from pathlib import Path

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


def extract_channel_number(file_name):
    match = re.search(r"\[(\d+)\s*(\w+)\]", file_name)
    if match:
        return int(match.group(1))
    return 0


def create_multichannel_audio_file():
    wav_files = [file for file in os.listdir(INPUT_PATH) if file.endswith(".wav")]

    channels = len(wav_files)
    channel_layout = (
        "quad"
        if channels == 4
        else "5.1"
        if channels == 6
        else "7.1"
        if channels == 8
        else None
    )
    join_audio_filter = (
        "[0:a][1:a][2:a][3:a]"
        if channels == 4
        else "[0:a][1:a][2:a][3:a][4:a][5:a]"
        if channels == 6
        else "[0:a][1:a][2:a][3:a][4:a][5:a][6:a][7:a]"
        if channels == 8
        else ""
    )

    input_args = []
    sorted_wav_files = sorted(wav_files, key=extract_channel_number)
    for wav_file in sorted_wav_files:
        input_args.extend(["-i", os.path.join(INPUT_PATH, wav_file)])

    subprocess.run(
        [
            "ffmpeg",
            *input_args,
            "-filter_complex",
            "{}join=inputs={}:channel_layout={}[a]".format(
                join_audio_filter, channels, channel_layout
            ),
            "-map",
            "[a]",
            "-c:a",
            CODEC,
            os.path.join(INPUT_PATH, f"{INPUT_PATH}.wav"),
        ]
    )


def get_codec():
    print("Getting codec...")

    if BIT_DEPTH == 16:
        codec = "pcm_s16le"
    elif BIT_DEPTH == 24:
        codec = "pcm_s24le"
    elif BIT_DEPTH == 32:
        codec = "pcm_s32le"
    else:
        raise ValueError(f"Unsupported bit depth: {BIT_DEPTH}")

    print(f"codec={codec}")
    print("Done.")

    return codec


def get_bit_depth():
    print("Extracting bit depth...")

    output = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=bits_per_raw_sample",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            os.path.join(INPUT_PATH, f"{INPUT_PATH} [1 FL].wav"),
        ]
    ).split()[0]
    bit_depth = int(output) if output != b"N/A" else 16

    print(f"bits_per_sample={bit_depth}")
    print("Done.")

    return bit_depth


def main():
    global BIT_DEPTH, CODEC
    BIT_DEPTH = get_bit_depth()
    CODEC = get_codec()

    create_multichannel_audio_file()


if __name__ == "__main__":
    main()
