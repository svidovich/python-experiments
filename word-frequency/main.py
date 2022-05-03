import argparse
import requests

from collections import Counter
from lxml import html

exclusions = [
    'a',
    'an',
    'and',
    'are',
    'as',
    'be',
    'by',
    'can',
    'do',
    'for',
    'if',
    'in',
    'is',
    'it',
    'not',
    'of',
    'on',
    'or',
    'that',
    'the',
    'this',
    'to',
    'will',
    'with',
    'you',
    'your',
]

def get_page_body(url: str) -> str:
    response = requests.get(url)
    parsed_content = html.fromstring(response.content)
    content_body = parsed_content.xpath('//body')[0].text_content()
    return content_body

def count_words(page_text: str) -> Counter:
    output = Counter()
    split_text = page_text.split(' ')
    split_text = [word.lower() for word in list(filter(None, split_text))]
    # This is better w/ defaultdict but im 2 lazy 2 remembr how
    for word in split_text:
        if word not in exclusions and word.isalpha():
            if word not in output:
                output[word] = 0
            else:
                output[word] += 1
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', required=True, type=str, help='The URL to eyeball')
    parser.add_argument('-t', '--top', required=False, type=int, default=10, help='The top n words to show, e.g. setting 5 will return the top 5 words on the page.')
    args = parser.parse_args()
    page_text = get_page_body(args.url)
    counts = count_words(page_text)
    for index, word_tuple in enumerate(counts.most_common(args.top)):
        word: str
        count: int
        word, count = word_tuple
        print(f'{index + 1}. {word}: {count}')

if __name__ == '__main__':
    main()