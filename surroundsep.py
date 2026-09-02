#!/usr/bin/env python3

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
import unicodedata

SUPPORTED_FILES = [
    ".wave",
    ".wav",
    ".flac",
    ".m4a",
]  # TODO: .m4a might be lossy -> double check if codec is TrueHD

ORTF_3D_LAYOUT = "ortf-3d"
ORTF_3D_CHANNELS = ("L", "R", "LS", "RS", "Lh", "Rh", "LSh", "RSh")
ORTF_3D_CHANNEL_SIGNATURE = re.compile(
    r"(?:^|[-_])l,r,ls,rs,lh,rh,lsh,rsh(?:[-_]|$)", re.IGNORECASE
)

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
parser.add_argument(
    "--layout",
    dest="CHANNEL_LAYOUT",
    choices=("auto", "7.1", ORTF_3D_LAYOUT),
    default="auto",
    help=(
        "the input channel layout; ORTF 3D is automatically detected from "
        "recognized filenames"
    ),
)
args = parser.parse_args()

INPUT_PATH = args.POSITIONAL_INPUT_PATH or args.INPUT_PATH
CHANNEL_LAYOUT_OVERRIDE = args.CHANNEL_LAYOUT
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


def is_ortf_3d_file(input_path):
    stem = os.path.splitext(os.path.basename(input_path))[0]

    if ORTF_3D_CHANNEL_SIGNATURE.search(stem):
        return True

    normalized_stem = re.sub(r"[^a-z0-9]", "", stem.lower())
    return "ortf3d" in normalized_stem


def split_ortf_3d_channels():
    split_inputs = "".join(f"[ortf_input_{index}]" for index in range(8))
    filters = [f"[0:a:0]asplit=8{split_inputs}"]
    filters.extend(
        f"[ortf_input_{index}]pan=mono|c0=c{index}[ortf_output_{index}]"
        for index in range(8)
    )

    command = [
        "ffmpeg",
        "-guess_layout_max",
        "0",
        "-i",
        INPUT_PATH,
        "-filter_complex",
        ";".join(filters),
    ]

    for index, channel_name in enumerate(ORTF_3D_CHANNELS):
        command.extend(
            [
                "-map",
                f"[ortf_output_{index}]",
                "-c:a",
                CODEC,
                os.path.join(
                    OUTPUT_PATH,
                    FILE_NAME,
                    f"{FILE_NAME} [{index + 1} {channel_name}].wav",
                ),
            ]
        )

    command.append("-y")
    subprocess.run(command, check=True)


def split_channels(channel_layout):
    if channel_layout == ORTF_3D_LAYOUT:
        split_ortf_3d_channels()
        return

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
        probed_layout = subprocess.check_output(
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
        ).decode("UTF-8").strip()

        if CHANNEL_LAYOUT_OVERRIDE != "auto":
            if channels != 8:
                raise ValueError(
                    f"{CHANNEL_LAYOUT_OVERRIDE} requires exactly 8 channels; "
                    f"found {channels}"
                )
            return channels, CHANNEL_LAYOUT_OVERRIDE

        if channels == 8 and is_ortf_3d_file(INPUT_PATH):
            return channels, ORTF_3D_LAYOUT

        return (
            channels,
            "quad"
            if "quad" in probed_layout
            else "5.1"
            if "5.1" in probed_layout
            else "7.1"
            if "7.1" in probed_layout
            else None,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running FFprobe: {e}")
        return None, None


def get_audio_stream_info():
    output = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,sample_fmt,bits_per_sample,bits_per_raw_sample",
            "-of",
            "json",
            INPUT_PATH,
        ]
    )

    try:
        streams = json.loads(output).get("streams", [])
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError("FFprobe returned invalid audio stream information") from error

    if not streams:
        raise ValueError("FFprobe did not return an audio stream")

    return streams[0]


def get_codec(stream_info=None):
    print("Getting codec...")

    source_codec = (stream_info or {}).get("codec_name")

    if source_codec in {"pcm_f32le", "pcm_f32be"}:
        codec = "pcm_f32le"
    elif source_codec in {"pcm_f64le", "pcm_f64be"}:
        codec = "pcm_f64le"
    elif BIT_DEPTH == 16:
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


def get_bit_depth(stream_info=None):
    print("Extracting bit depth...")

    if stream_info is None:
        stream_info = get_audio_stream_info()

    bit_depth = None
    for field in ("bits_per_raw_sample", "bits_per_sample"):
        try:
            candidate = int(stream_info.get(field, 0))
        except (TypeError, ValueError):
            continue

        if candidate > 0:
            bit_depth = candidate
            break

    if bit_depth is None:
        raise ValueError("Unable to determine audio bit depth from FFprobe output")

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
        if channel_layout == ORTF_3D_LAYOUT:
            print(f"Channel layout: ORTF 3D ({', '.join(ORTF_3D_CHANNELS)})")
        else:
            print(f"Channel layout: {channel_layout}")

        if os.path.exists(os.path.join(OUTPUT_PATH, FILE_NAME)):
            print("Working dir already exists.")
        else:
            os.mkdir(os.path.join(OUTPUT_PATH, FILE_NAME))
            print("Working dir created.")

        stream_info = get_audio_stream_info()

        global BIT_DEPTH, CODEC
        BIT_DEPTH = get_bit_depth(stream_info)
        CODEC = get_codec(stream_info)

        split_channels(channel_layout)
    else:
        if channels is not None and channels > 8:
            print("Too many channels! You need to downmix to 7.1 :)")
        elif channels == 8:
            print(
                "Unknown 8-channel layout. Use --layout 7.1 or "
                "--layout ortf-3d."
            )
        else:
            print("Failed to retrieve channel information.")


if __name__ == "__main__":
    main()
