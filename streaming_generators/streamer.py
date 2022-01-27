import inspect

from io import TextIOWrapper
from typing import Generator

# yapf: disable
generator_just_created = lambda g: inspect.getgeneratorstate(g) == inspect.GEN_CREATED

def sender(line: str, target: Generator):
    if generator_just_created(target):
        target.send(None)
    target.send(line)


def receiver(suffix: str, file_handle: TextIOWrapper):
    while True:
        line = (yield)
        file_handle.write(f'{line}-{suffix}\n')


def main():
    test_strings = ['this', 'is', 'a', 'data', 'source']
    with open('coolfile', 'w') as file_handle:
        for string in test_strings:
            sender(string, receiver('mewoth', file_handle))


if __name__ == '__main__':
    main()
