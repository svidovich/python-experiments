import argparse
import pika


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--queue-url', help="Where to send your message")
    parser.add_agument('-m', '--message', help="The message to send")
    args = parser.parse_args()