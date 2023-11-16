"""
collect_words.py

Given the document output from pare.py,
do some... stuff.
"""
# pylint: disable=unspecified-encoding,missing-function-docstring

import argparse
import re
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET

WIKTIONARY_SECTION_HEADER = re.compile(r"^={2}[A-Za-z\-]+={2}$")
SERBO_CROATIAN = "Serbo-Croatian"  # YES

WIKTIONARY_SERBO_CROATIAN_HEADER = re.compile(r"^={2}Serbo-Croatian={2}$")
CONJUGATION_HEADER = re.compile(r"^={2,5}Conjugation={2,5}$")
VERB_HEADER = re.compile(r"^={2,5}Verb={2,5}$")

WIKTIONARY_ANY_HEADER = re.compile(r"^=")

WIKTIONARY_NS = "{http://www.mediawiki.org/xml/export-0.10/}"
WIKTIONARY_PAGE_TAG = f"{WIKTIONARY_NS}page"
WIKTIONARY_REVISION_TAG = f"{WIKTIONARY_NS}revision"
WIKTIONARY_TEXT_TAG = f"{WIKTIONARY_NS}text"
WIKTIONARY_TITLE_TAG = f"{WIKTIONARY_NS}title"


# NOTE
# Languages that appeared in my filtered list
# Yours may differ
GERMANE_LANGUAGES = {
    "Albanian",
    "Apolista",
    "Arawak",
    "Asturian",
    "Azerbaijani",
    "Basque",
    "Bassa",
    "Bavarian",
    "Blagar",
    "Bourguignon",
    "Catalan",
    "Catawba",
    "Cebuano",
    "Choctaw",
    "Cornish",
    "Czech",
    "Danish",
    "Dutch",
    "Emilian",
    "English",
    "Esperanto",
    "Estonian",
    "Faroese",
    "Finnish",
    "French",
    "Gallurese",
    "Garo",
    "German",
    "Huba",
    "Ibaloi",
    "Icelandic",
    "Ido",
    "Igbo",
    "Indonesian",
    "Italian",
    "Ivatan",
    "Javanese",
    "Kabuverdianu",
    "Kamba",
    "Kambera",
    "Kapampangan",
    "Kaurna",
    "Lashi",
    "Latin",
    "Latvian",
    "Lindu",
    "Lithuanian",
    "Malay",
    "Mansaka",
    "Marshallese",
    "Occitan",
    "Pali",
    "Phuthi",
    "Pitjantjatjara",
    "Polish",
    "Portuguese",
    "Romanian",
    "Rukai",
    "Samoan",
    SERBO_CROATIAN,
    "Sicilian",
    "Slovak",
    "Slovene",
    "Spanish",
    "Sumerian",
    "Swahili",
    "Tagalog",
    "Tahitian",
    "Ternate",
    "Tumbuka",
    "Turkish",
    "Turkmen",
    "Venetian",
    "Vietnamese",
    "Walloon",
    "Waray-Waray",
    "Welsh",
    "Xhosa",
    "Yogad",
    "Yoruba",
    "Zazaki",
}

# Srsly what even are these lol
GOOFY_CHARS = {
    "ā": "a",
    "è": "e",
    "ȅ": "e",
    "í": "i",
    "ȉ": "i",
    "ȋ": "i",
    "ū": "u",
    "ȕ": "u",
}


def clean_wiki_header(header: str) -> str:
    return header.strip("=").strip()


def header_is_language(header: str) -> bool:
    return clean_wiki_header(header=header) in GERMANE_LANGUAGES


def iterate_xml(xml_path: str) -> None:
    context = ET.iterparse(xml_path, events=("start", "end"))
    conjugations_missing = 0
    for i, (event, element) in enumerate(context):
        if i == 0:
            root = element
        # This should look familiar. It's copypasta.
        if event == "end" and element.tag == WIKTIONARY_PAGE_TAG:
            # Try and get a revision element,l
            word = element.find(WIKTIONARY_TITLE_TAG).text
            revision = element.find(WIKTIONARY_REVISION_TAG)
            if revision is None:
                continue
            # and from there, the text body of the article.
            text = revision.find(WIKTIONARY_TEXT_TAG)
            if text is None:
                continue
            text_lines = text.text.splitlines()
            verb_section = []
            verb_found = False
            conjugation_section = []
            conjugation_found = False
            for index, line in enumerate(text_lines):
                if WIKTIONARY_SERBO_CROATIAN_HEADER.match(line) is not None:
                    # I could make these functions, but meh.
                    # Chomp this section until we find conjugations.
                    # Chomp the conjugations.
                    j = index
                    while True:
                        if (
                            not conjugation_found
                            and CONJUGATION_HEADER.match(text_lines[j]) is not None
                        ):
                            conjugation_found = True
                            k = j + 1
                            while True:
                                if not WIKTIONARY_ANY_HEADER.match(text_lines[k]):
                                    conjugation_section.append(text_lines[k])
                                else:
                                    break
                                if k + 1 >= len(text_lines):
                                    break
                                k += 1
                        if j + 1 >= len(text_lines):
                            break
                        j += 1
                    j = index
                    while True:
                        if (
                            not verb_found
                            and VERB_HEADER.match(text_lines[j]) is not None
                        ):
                            verb_found = True
                            k = j + 1
                            while True:
                                if not WIKTIONARY_ANY_HEADER.match(text_lines[k]):
                                    verb_section.append(text_lines[k])
                                else:
                                    break
                                if k + 1 >= len(text_lines):
                                    break
                                k += 1
                        if j + 1 >= len(text_lines):
                            break
                        j += 1

                    # print(clean_wiki_header(line))
            if not conjugation_section:
                print(f"No conjugation section for {word}!")
                conjugations_missing += 1
            breakpoint()
            print()
        root.clear()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input-file", help="The XML file to read.", required=True
    )
    args = parser.parse_args()
    iterate_xml(xml_path=args.input_file)


if __name__ == "__main__":
    main()
