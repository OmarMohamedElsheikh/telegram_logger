import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-jn", "--just-notify", action="store_true")
    group.add_argument("-jnr", "--just-notify-running", action="store_true")
    group.add_argument("-nn", "--no-notification", action="store_true")

    return parser.parse_args()

