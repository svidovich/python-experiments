"""
pare.py

Given a file containing a list of "words of interest" and
a Wiktionary XML, pare the XML down to only the pages that
match our words of interest, and save it off to a new location.
"""
# pylint: disable=unspecified-encoding,missing-function-docstring

import argparse
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from typing import Iterator

WIKTIONARY_SECTION_HEADER = re.compile("^={2}[A-Za-z\-]+={2}$")

WIKTIONARY_NS = "{http://www.mediawiki.org/xml/export-0.10/}"
WIKTIONARY_PAGE_TAG = f"{WIKTIONARY_NS}page"
WIKTIONARY_REVISION_TAG = f"{WIKTIONARY_NS}revision"
WIKTIONARY_TEXT_TAG = f"{WIKTIONARY_NS}text"
WIKTIONARY_TITLE_TAG = f"{WIKTIONARY_NS}title"


def load_words(path: str) -> set[str]:
    """
    Given a path to a file, loads a newline-delimited
    list of words into a set.
    """
    words = set()
    with open(path, "r") as file_handle:
        for line in file_handle.readlines():
            words.add(line.strip())
    return words


def generate_entries(xml_path: str, word_list_path: str) -> Iterator[Element]:
    """
    Given file paths... TODO
    """
    words = load_words(word_list_path)

    context = ET.iterparse(xml_path, events=("start", "end"))

    for index, (event, element) in enumerate(context):
        # Get the root element.
        if index == 0:
            root = element
        if event == "end" and element.tag == WIKTIONARY_PAGE_TAG:
            # We've found a page. Grab the title.
            title = element.find(WIKTIONARY_TITLE_TAG)
            title_text = title.text if title is not None else None

            # If the title text matches one of the words we're looking for,
            if title_text is not None and title_text in words:
                # Try and get a revision element,
                revision = element.find(WIKTIONARY_REVISION_TAG)
                if revision is None:
                    continue
                # and from there, the text body of the article.
                text = revision.find(WIKTIONARY_TEXT_TAG)
                if text is None:
                    continue
                page_container = Element("pagecontainer")
                page_container.append(element)
                yield page_container

        root.clear()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            'Given a file containing a list of "words of interest" '
            "and a Wiktionary XML, pare the XML down to only the pages "
            "that match our words of interest, and save it off to a new "
            "location."
        )
    )
    parser.add_argument(
        "-w",
        "--word-list-file",
        required=True,
        help="Path to a newline-delimited list of words to be looked up.",
    )
    parser.add_argument(
        "-x",
        "--wiktionary-xml-file",
        required=True,
        help="Path to a wiktionary XML file.",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        required=False,
        default="filtered.xml",
        help="Where to write the filtered XML",
    )

    args = parser.parse_args()

    new_parent = Element("parent")
    for element in generate_entries(args.wiktionary_xml_file, args.word_list_file):
        new_parent.append(element)

    tree = ET.ElementTree(new_parent)
    tree.write(args.output_file)


if __name__ == "__main__":
    main()
