import inspect

from typing import Generator

# yapf: disable
generator_just_created = lambda g: inspect.getgeneratorstate(g) == inspect.GEN_CREATED

def sender(line: str, target: Generator):
    if generator_just_created(target):
        target.send(None)
    target.send(line)


def receiver(suffix: str):
    while True:
        line = (yield)
        print(f'{line}-{suffix}')


def main():
    test_strings = ['this', 'is', 'a', 'data', 'source']
    for string in test_strings:
        sender(string, receiver('mewoth'))


if __name__ == '__main__':
    main()
