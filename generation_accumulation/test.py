import argparse
import time
from math import floor
from random import choice

from module import accumulation, generation

ASCII_USABLE_MINIMUM = 33
ASCII_USABLE_MAXIMUM = 126


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--iteration-count', type=int, required=False, default=100000, help='How many iterations to go through in testing')
    args = parser.parse_args()
    iteration_count = args.iteration_count
    list_of_strings = list()
    for _ in range(iteration_count):
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

    _ = input('Press any key to exit.')


if __name__ == '__main__':
    main()
