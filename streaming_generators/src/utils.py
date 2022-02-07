import inspect
from typing import Iterator, Generator

# yapf: disable
generator_just_created = lambda g: inspect.getgeneratorstate(g) == inspect.GEN_CREATED


# yapf: enable
def prime_generator(target: Generator):
    if generator_just_created(target):
        target.send(None)


def broadcast(targets: Iterator[Generator]):
    """
    Send data to multiple target generators.
    """
    while True:
        data = (yield)
        for target in targets:
            prime_generator(target)
            target.send(data)
