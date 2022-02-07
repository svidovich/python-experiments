import inspect
from typing import Iterator, Generator

# yapf: disable
generator_just_created = lambda g: inspect.getgeneratorstate(g) == inspect.GEN_CREATED

# David Beazley is a god.
# http://dabeaz.com/coroutines/coroutine.py
def coroutine(function: Generator):
    def prime(*args, **kwargs):
        coro = function(*args, **kwargs)
        coro.next()
    return prime


# yapf: enable
def prime_generator(target: Generator):
    if generator_just_created(target):
        target.send(None)


@coroutine
def broadcast(targets: Iterator[Generator]):
    """
    Send data to multiple target generators.
    """
    while True:
        data = (yield)
        for target in targets:
            prime_generator(target)
            target.send(data)
