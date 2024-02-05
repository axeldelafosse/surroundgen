#!/usr/bin/env python3

import os
import re
import sys
import subprocess as sp
from os.path import basename


# TODO: use `ffprobe -i fname -print_format json -show_chapters -loglevel error` instead
def parse_chapters(filename):
    chapters = []
    command = ["ffmpeg", "-i", filename]
    output = ""
    m = None
    title = None
    chapter_match = None
    try:
        # ffmpeg requires an output file and so it errors
        # when it does not get one so we need to capture stderr,
        # not stdout.
        output = sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
    except sp.CalledProcessError as e:
        output = e.output

    num = 1

    for line in iter(output.splitlines()):
        x = re.match(r".*title.*: (.*)", line)

        if x == None:
            m1 = re.match(
                r".*Chapter #(\d+:\d+): start (\d+\.\d+), end (\d+\.\d+).*", line
            )
            title = None
        else:
            title = x.group(1)

        if m1 != None:
            chapter_match = m1

        if title != None and chapter_match != None:
            m = chapter_match
        else:
            m = None

        if m != None:
            chapters.append(
                {
                    "name": str(num) + " - " + title,
                    "start": m.group(2),
                    "end": m.group(3),
                }
            )
            num += 1

    return chapters


def get_chapters():
    filename = sys.argv[1]

    chapters = parse_chapters(filename)
    newdir, fext = os.path.splitext(basename(filename))

    workingdir = os.path.join(os.getcwd(), newdir)
    if os.path.exists(workingdir):
        print("Working dir already exists.")
    else:
        os.mkdir(workingdir)
        print("Working dir created.")

    for chap in chapters:
        chap["name"] = chap["name"].replace("/", ":")
        chap["name"] = chap["name"].replace("'", "'")
        print("start:" + chap["start"])
        chap["output"] = os.path.join(
            workingdir, re.sub("[^-a-zA-Z0-9_.():' ]+", "", chap["name"]) + ".flac"
        )
        chap["input"] = os.path.join(os.getcwd(), filename)
        print(chap["output"])
    return chapters


def convert_chapters(chapters):
    for chap in chapters:
        print("start:" + chap["start"])
        print(chap)

        if os.path.isfile(chap["output"]):
            continue

        command = [
            "ffmpeg",
            "-i",
            chap["input"],
            "-ss",
            chap["start"],
            "-to",
            chap["end"],
            "-c:a",
            "flac",
            chap["output"],
        ]
        try:
            sp.check_output(command, stderr=sp.STDOUT, universal_newlines=True)
        except sp.CalledProcessError as e:
            raise RuntimeError(
                "command '{}' return with error (code {}): {}".format(
                    e.cmd, e.returncode, e.output
                )
            )


# TODO: select TrueHD stream
def main():
    chapters = get_chapters()
    convert_chapters(chapters)


if __name__ == "__main__":
    main()
