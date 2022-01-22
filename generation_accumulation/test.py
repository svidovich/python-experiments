from audioop import mul
from math import floor
import time
from random import choice

from module import accumulation, generation

ITERATION_COUNT = 100000

ASCII_USABLE_MINIMUM = 33
ASCII_USABLE_MAXIMUM = 126


def main():
    list_of_strings = list()
    for number in range(ITERATION_COUNT):
        list_of_strings.append(
            chr(choice(list(range(ASCII_USABLE_MINIMUM,
                                  ASCII_USABLE_MAXIMUM)))))

    _ = input("Press any key to start test for accumulation")
    start = time.time()
    for string in accumulation(list_of_strings):
        print(string)
    end = time.time()
    print(f'Printed in {end - start}s')

    _ = input("Press any key to start test for generation")
    start = time.time()
    for string in generation(list_of_strings):
        print(string)
    end = time.time()
    print(f'Printed in {end - start}s')


if __name__ == '__main__':
    main()
