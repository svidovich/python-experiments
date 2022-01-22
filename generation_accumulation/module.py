from typing import Generator, List


def generation(list_of_strings: List[str]) -> Generator:
    for string in list_of_strings:
        yield f'{string}, but modified'


def accumulation(list_of_strings: List[str]) -> List[str]:
    output_list = list()
    for string in list_of_strings:
        output_list.append(f'{string}, but modified')
    return output_list
