import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent2 = os.path.dirname(parent)
sys.path.append(parent2)

import mkv2flac


def main():
    mkv2flac.main()


if __name__ == "__main__":
    main()
