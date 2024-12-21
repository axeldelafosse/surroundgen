import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
parent2 = os.path.dirname(parent)
sys.path.append(parent2)

import mkv2mlp


def main():
    mkv2mlp.main()


if __name__ == "__main__":
    main()
