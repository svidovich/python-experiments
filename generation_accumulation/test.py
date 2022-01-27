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
    parser.add_argument('-a', '--only-accumulation', action='store_true', required=False, help='Only test accumulation')
    parser.add_argument('-g', '--only-generation', action='store_true', required=False, help='Only test generation')
    args = parser.parse_args()
    iteration_count: int = args.iteration_count
    only_accumulation: bool = args.only_accumulation
    only_generation: bool = args.only_generation
    if only_accumulation and only_generation:
        print("'only-accumulation' and 'only-generation' are mutually exclusive. One or the other, not both.")
        exit(0)

    list_of_strings = list()
    print(f'Generating a test list of {iteration_count} strings...')
    for _ in range(iteration_count):
        list_of_strings.append(
            chr(choice(list(range(ASCII_USABLE_MINIMUM,
                                  ASCII_USABLE_MAXIMUM)))))

    if not only_generation:
        _ = input("Press any key to start test for accumulation")
        start = time.time()
        for string in accumulation(list_of_strings):
            print(string)
        end = time.time()
        print(f'Printed in {end - start}s')

    if not only_accumulation:
        _ = input("Press any key to start test for generation")
        start = time.time()
        for string in generation(list_of_strings):
            print(string)
        end = time.time()
        print(f'Printed in {end - start}s')

    _ = input('Press any key to exit.')


if __name__ == '__main__':
    main()
