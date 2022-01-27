from typing import Generator


def sender(line: str, target: Generator):
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
