import inspect
from typing import Generator

# yapf: disable
generator_just_created = lambda g: inspect.getgeneratorstate(g) == inspect.GEN_CREATED


# yapf: enable
def prime_generator(target: Generator):
    if generator_just_created(target):
        target.send(None)
