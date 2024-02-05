#!/usr/bin/env python3

import argparse
import subprocess
import os
from pathlib import Path
import unicodedata

SUPPORTED_FILES = [
    ".wave",
    ".wav",
    ".flac",
    ".m4a",
]  # TODO: .m4a might be lossy -> double check if codec is TrueHD

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


def split_channels(channel_layout):
    if channel_layout == "quad":
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                INPUT_PATH,
                "-filter_complex",
                f"channelsplit=channel_layout={channel_layout}[FL][FR][SL][SR]",
                "-map",
                "[FL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [1 FL].wav"),
                "-map",
                "[FR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [2 FR].wav"),
                "-map",
                "[SL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [5 SL].wav"),
                "-map",
                "[SR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [6 SR].wav"),
                "-y",
            ]
        )

    if channel_layout == "5.1":
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                INPUT_PATH,
                "-filter_complex",
                f"channelsplit=channel_layout={channel_layout}[FL][FR][FC][LFE][SL][SR]",
                "-map",
                "[FL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [1 FL].wav"),
                "-map",
                "[FR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [2 FR].wav"),
                "-map",
                "[FC]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [3 FC].wav"),
                "-map",
                "[LFE]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [4 LFE].wav"),
                "-map",
                "[SL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [5 SL].wav"),
                "-map",
                "[SR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [6 SR].wav"),
                "-y",
            ]
        )

    if channel_layout == "7.1" and FILE_EXTENSION == ".wav":
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                INPUT_PATH,
                "-filter_complex",
                f"channelsplit=channel_layout={channel_layout}[FL][FR][FC][LFE][SL][SR][BL][BR]",  # reverse SL / SR and BL / BR for wav
                "-map",
                "[FL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [1 FL].wav"),
                "-map",
                "[FR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [2 FR].wav"),
                "-map",
                "[FC]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [3 FC].wav"),
                "-map",
                "[LFE]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [4 LFE].wav"),
                "-map",
                "[SL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [5 SL].wav"),
                "-map",
                "[SR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [6 SR].wav"),
                "-map",
                "[BL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [7 BL].wav"),
                "-map",
                "[BR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [8 BR].wav"),
                "-y",
            ]
        )

    if channel_layout == "7.1" and FILE_EXTENSION != ".wav":
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                INPUT_PATH,
                "-filter_complex",
                f"channelsplit=channel_layout={channel_layout}[FL][FR][FC][LFE][BL][BR][SL][SR]",
                "-map",
                "[FL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [1 FL].wav"),
                "-map",
                "[FR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [2 FR].wav"),
                "-map",
                "[FC]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [3 FC].wav"),
                "-map",
                "[LFE]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [4 LFE].wav"),
                "-map",
                "[SL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [5 SL].wav"),
                "-map",
                "[SR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [6 SR].wav"),
                "-map",
                "[BL]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [7 BL].wav"),
                "-map",
                "[BR]",
                "-c:a",
                CODEC,
                os.path.join(OUTPUT_PATH, FILE_NAME, f"{FILE_NAME} [8 BR].wav"),
                "-y",
            ]
        )


def get_audio_channels_info():
    try:
        channels = int(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "a",
                    "-show_entries",
                    "stream=channels",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    INPUT_PATH,
                ]
            )
        )
        channel_layout = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=channel_layout",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                INPUT_PATH,
            ]
        ).decode("UTF-8")
        return (
            channels,
            "quad"
            if "quad" in channel_layout
            else "5.1"
            if "5.1" in channel_layout
            else "7.1"
            if "7.1" in channel_layout
            else "7.1"
            if channels == 8 and FILE_EXTENSION == ".wav"
            else None,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running FFprobe: {e}")
        return None, None


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

    bit_depth = int(
        subprocess.check_output(
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
                INPUT_PATH,
            ]
        ).split()[0]
    )

    print(f"bits_per_sample={bit_depth}")
    print("Done.")

    return bit_depth


def main():
    global BASE_PATH, FILE_EXTENSION
    BASE_PATH = os.path.basename(INPUT_PATH)
    FILE_EXTENSION = os.path.splitext(BASE_PATH)[1]

    global FILE_NAME, INPUT_DIR, FILE_PATH
    FILE_NAME = strip_accents(BASE_PATH.removesuffix(FILE_EXTENSION))

    channels, channel_layout = get_audio_channels_info()

    if channels is not None and channel_layout is not None:
        print(f"Number of channels: {channels}")
        print(f"Channel layout: {channel_layout}")

        if os.path.exists(os.path.join(OUTPUT_PATH, FILE_NAME)):
            print("Working dir already exists.")
        else:
            os.mkdir(os.path.join(OUTPUT_PATH, FILE_NAME))
            print("Working dir created.")

        global BIT_DEPTH, CODEC
        BIT_DEPTH = get_bit_depth()
        CODEC = get_codec()

        split_channels(channel_layout)
    else:
        if channels is not None and channels > 8:
            print("Too many channels! You need to downmix to 7.1 :)")
        else:
            print("Failed to retrieve channel information.")


if __name__ == "__main__":
    main()
