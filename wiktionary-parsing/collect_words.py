"""
collect_words.py

Given the document output from pare.py,
do some... stuff.
"""
# pylint: disable=unspecified-encoding,missing-function-docstring

import argparse
import json
import re
from enum import Enum
from typing import Callable, Iterator, NamedTuple, Optional
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


class Tense(str, Enum):
    """
    Grammatical Tenses for Serbo-Croatian
    """

    # Present Tense
    FIRST_PERSON_PRESENT_SINGULAR = "first_person_present_singular"
    SECOND_PERSON_PRESENT_SINGULAR = "second_person_present_singular"
    THIRD_PERSON_PRESENT_SINGULAR = "third_person_present_singular"
    FIRST_PERSON_PRESENT_PLURAL = "first_person_present_plural"
    SECOND_PERSON_PRESENT_PLURAL = "second_person_present_plural"
    THIRD_PERSON_PRESENT_PLURAL = "third_person_present_plural"
    # Future Tense
    FIRST_PERSON_FUTURE_SINGULAR_I = "first_person_future_singular_i"
    SECOND_PERSON_FUTURE_SINGULAR_I = "second_person_future_singular_i"
    THIRD_PERSON_FUTURE_SINGULAR_I = "third_person_future_singular_i"
    FIRST_PERSON_FUTURE_PLURAL_I = "first_person_future_plural_i"
    SECOND_PERSON_FUTURE_PLURAL_I = "second_person_future_plural_i"
    THIRD_PERSON_FUTURE_PLURAL_I = "third_person_future_plural_i"
    # "Unclear" Future Tense ( he will have, etc. )
    FIRST_PERSON_FUTURE_SINGULAR_II = "first_person_future_singular_ii"
    SECOND_PERSON_FUTURE_SINGULAR_II = "second_person_future_singular_ii"
    THIRD_PERSON_FUTURE_SINGULAR_II = "third_person_future_singular_ii"
    FIRST_PERSON_FUTURE_PLURAL_II = "first_person_future_plural_ii"
    SECOND_PERSON_FUTURE_PLURAL_II = "second_person_future_plural_ii"
    THIRD_PERSON_FUTURE_PLURAL_II = "third_person_future_plural_ii"
    # Past Tense
    FIRST_PERSON_PAST_PERFECT_SINGULAR = "first_person_past_perfect_singular"
    SECOND_PERSON_PAST_PERFECT_SINGULAR = "second_person_past_perfect_singular"
    THIRD_PERSON_PAST_PERFECT_SINGULAR = "third_person_past_perfect_singular"
    FIRST_PERSON_PAST_PERFECT_PLURAL = "first_person_past_perfect_plural"
    SECOND_PERSON_PAST_PERFECT_PLURAL = "second_person_past_perfect_plural"
    THIRD_PERSON_PAST_PERFECT_PLURAL = "third_person_past_perfect_plural"
    # Completed Past Tense ( he had... )
    FIRST_PERSON_PAST_PLUPERFECT_SINGULAR = "first_person_past_pluperfect_singular"
    SECOND_PERSON_PAST_PLUPERFECT_SINGULAR = "second_person_past_pluperfect_singular"
    THIRD_PERSON_PAST_PLUPERFECT_SINGULAR = "third_person_past_pluperfect_singular"
    FIRST_PERSON_PAST_PLUPERFECT_PLURAL = "first_person_past_pluperfect_plural"
    SECOND_PERSON_PAST_PLUPERFECT_PLURAL = "second_person_past_pluperfect_plural"
    THIRD_PERSON_PAST_PLUPERFECT_PLURAL = "third_person_past_pluperfect_plural"
    # Imperfect Past Tense ( it used to ... )
    FIRST_PERSON_PAST_IMPERFECT_SINGULAR = "first_person_past_imperfect_singular"
    SECOND_PERSON_PAST_IMPERFECT_SINGULAR = "second_person_past_imperfect_singular"
    THIRD_PERSON_PAST_IMPERFECT_SINGULAR = "third_person_past_imperfect_singular"
    FIRST_PERSON_PAST_IMPERFECT_PLURAL = "first_person_past_imperfect_plural"
    SECOND_PERSON_PAST_IMPERFECT_PLURAL = "second_person_past_imperfect_plural"
    THIRD_PERSON_PAST_IMPERFECT_PLURAL = "third_person_past_imperfect_plural"
    # ??? Who knows what this does ??? it's intentionally vague
    FIRST_PERSON_PAST_AORIST_SINGULAR = "first_person_past_aorist_singular"
    SECOND_PERSON_PAST_AORIST_SINGULAR = "second_person_past_aorist_singular"
    THIRD_PERSON_PAST_AORIST_SINGULAR = "third_person_past_aorist_singular"
    FIRST_PERSON_PAST_AORIST_PLURAL = "first_person_past_aorist_plural"
    SECOND_PERSON_PAST_AORIST_PLURAL = "second_person_past_aorist_plural"
    THIRD_PERSON_PAST_AORIST_PLURAL = "third_person_past_aorist_plural"
    # I would...
    FIRST_PERSON_CONDITIONAL_I_SINGULAR = "first_person_conditional_i_singular"
    SECOND_PERSON_CONDITIONAL_I_SINGULAR = "second_person_conditional_i_singular"
    THIRD_PERSON_CONDITIONAL_I_SINGULAR = "third_person_conditional_i_singular"
    FIRST_PERSON_CONDITIONAL_I_PLURAL = "first_person_conditional_i_plural"
    SECOND_PERSON_CONDITIONAL_I_PLURAL = "second_person_conditional_i_plural"
    THIRD_PERSON_CONDITIONAL_I_PLURAL = "third_person_conditional_i_plural"
    FIRST_PERSON_CONDITIONAL_II_SINGULAR = "first_person_conditional_ii_singular"
    SECOND_PERSON_CONDITIONAL_II_SINGULAR = "second_person_conditional_ii_singular"
    THIRD_PERSON_CONDITIONAL_II_SINGULAR = "third_person_conditional_ii_singular"
    FIRST_PERSON_CONDITIONAL_II_PLURAL = "first_person_conditional_ii_plural"
    SECOND_PERSON_CONDITIONAL_II_PLURAL = "second_person_conditional_ii_plural"
    THIRD_PERSON_CONDITIONAL_II_PLURAL = "third_person_conditional_ii_plural"
    # Commands
    FIRST_PERSON_IMPERATIVE_SINGULAR = "first_person_imperative_singular"
    FIRST_PERSON_IMPERATIVE_PLURAL = "first_person_imperative_plural"
    SECOND_PERSON_IMPERATIVE_PLURAL = "second_person_imperative_plural"
    # I have / he has / we have
    ACTIVE_PAST_PARTICIPLE = "active_past_participle"


TENSE_BUILDERS: dict[Tense, Callable[[dict[str, str]], Optional[str]]] = {
    Tense.FIRST_PERSON_PRESENT_SINGULAR: lambda c: c.get("pr.1s"),
    Tense.SECOND_PERSON_PRESENT_SINGULAR: lambda c: c.get("pr.2s"),
    Tense.THIRD_PERSON_PRESENT_SINGULAR: lambda c: c.get("pr.3s"),
    Tense.FIRST_PERSON_PRESENT_PLURAL: lambda c: c.get("pr.1p"),
    Tense.SECOND_PERSON_PRESENT_PLURAL: lambda c: c.get("pr.2p"),
    Tense.THIRD_PERSON_PRESENT_PLURAL: lambda c: c.get("pr.3p"),
    Tense.FIRST_PERSON_FUTURE_SINGULAR_I: lambda c: c["f1.hr"] + " ću"
    if c.get("f1.hr") is not None
    else None,
    Tense.SECOND_PERSON_FUTURE_SINGULAR_I: lambda c: c["f1.hr"] + " ćeš"
    if c.get("f1.hr") is not None
    else None,
    Tense.THIRD_PERSON_FUTURE_SINGULAR_I: lambda c: c["f1.hr"] + " će"
    if c.get("f1.hr") is not None
    else None,
    Tense.FIRST_PERSON_FUTURE_PLURAL_I: lambda c: c["f1.hr"] + " ćemo"
    if c.get("f1.hr") is not None
    else None,
    Tense.SECOND_PERSON_FUTURE_PLURAL_I: lambda c: c["f1.hr"] + " ćete"
    if c.get("f1.hr") is not None
    else None,
    Tense.THIRD_PERSON_FUTURE_PLURAL_I: lambda c: c["f1.hr"] + " će"
    if c.get("f1.hr") is not None
    else None,
    Tense.FIRST_PERSON_FUTURE_SINGULAR_II: lambda c: "budem " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.SECOND_PERSON_FUTURE_SINGULAR_II: lambda c: "budeš " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.THIRD_PERSON_FUTURE_SINGULAR_II: lambda c: "bude " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.FIRST_PERSON_FUTURE_PLURAL_II: lambda c: "budemo " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.SECOND_PERSON_FUTURE_PLURAL_II: lambda c: "budete " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.THIRD_PERSON_FUTURE_PLURAL_II: lambda c: "budu " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.FIRST_PERSON_PAST_PERFECT_SINGULAR: lambda c: c["app.ms"] + " sam"
    if c.get("app.ms") is not None
    else None,
    Tense.SECOND_PERSON_PAST_PERFECT_SINGULAR: lambda c: c["app.ms"] + " si"
    if c.get("app.ms") is not None
    else None,
    Tense.THIRD_PERSON_PAST_PERFECT_SINGULAR: lambda c: c["app.ms"] + " je"
    if c.get("app.ms") is not None
    else None,
    Tense.FIRST_PERSON_PAST_PERFECT_PLURAL: lambda c: c["app.mp"] + " smo"
    if c.get("app.mp") is not None
    else None,
    Tense.SECOND_PERSON_PAST_PERFECT_PLURAL: lambda c: c["app.mp"] + " ste"
    if c.get("app.mp") is not None
    else None,
    Tense.THIRD_PERSON_PAST_PERFECT_PLURAL: lambda c: c["app.mp"] + " su"
    if c.get("app.mp") is not None
    else None,
    Tense.FIRST_PERSON_PAST_PLUPERFECT_SINGULAR: lambda c: "bio sam " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.SECOND_PERSON_PAST_PLUPERFECT_SINGULAR: lambda c: "bio si " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.THIRD_PERSON_PAST_PLUPERFECT_SINGULAR: lambda c: "bio je " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.FIRST_PERSON_PAST_PLUPERFECT_PLURAL: lambda c: "bili smo " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.SECOND_PERSON_PAST_PLUPERFECT_PLURAL: lambda c: "bili ste " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.THIRD_PERSON_PAST_PLUPERFECT_PLURAL: lambda c: "bili su " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.FIRST_PERSON_PAST_IMPERFECT_SINGULAR: lambda c: c.get("impf.1s"),
    Tense.SECOND_PERSON_PAST_IMPERFECT_SINGULAR: lambda c: c.get("impf.2s"),
    Tense.THIRD_PERSON_PAST_IMPERFECT_SINGULAR: lambda c: c.get("impf.3s"),
    Tense.FIRST_PERSON_PAST_IMPERFECT_PLURAL: lambda c: c.get("impf.1p"),
    Tense.SECOND_PERSON_PAST_IMPERFECT_PLURAL: lambda c: c.get("impf.2p"),
    Tense.THIRD_PERSON_PAST_IMPERFECT_PLURAL: lambda c: c.get("impf.3p"),
    Tense.FIRST_PERSON_PAST_AORIST_SINGULAR: lambda c: c.get("a.1s"),
    Tense.SECOND_PERSON_PAST_AORIST_SINGULAR: lambda c: c.get("a.2s"),
    Tense.THIRD_PERSON_PAST_AORIST_SINGULAR: lambda c: c.get("a.3s"),
    Tense.FIRST_PERSON_PAST_AORIST_PLURAL: lambda c: c.get("a.1p"),
    Tense.SECOND_PERSON_PAST_AORIST_PLURAL: lambda c: c.get("a.2p"),
    Tense.THIRD_PERSON_PAST_AORIST_PLURAL: lambda c: c.get("a.3p"),
    Tense.FIRST_PERSON_CONDITIONAL_I_SINGULAR: lambda c: c["app.ms"] + " bih"
    if c.get("app.ms") is not None
    else None,
    Tense.SECOND_PERSON_CONDITIONAL_I_SINGULAR: lambda c: c["app.ms"] + " bi"
    if c.get("app.ms") is not None
    else None,
    Tense.THIRD_PERSON_CONDITIONAL_I_SINGULAR: lambda c: c["app.ms"] + " bi"
    if c.get("app.ms") is not None
    else None,
    Tense.FIRST_PERSON_CONDITIONAL_I_PLURAL: lambda c: c["app.mp"] + " bismo"
    if c.get("app.mp") is not None
    else None,
    Tense.SECOND_PERSON_CONDITIONAL_I_PLURAL: lambda c: c["app.mp"] + " biste"
    if c.get("app.mp") is not None
    else None,
    Tense.THIRD_PERSON_CONDITIONAL_I_PLURAL: lambda c: c["app.mp"] + " bi"
    if c.get("app.mp") is not None
    else None,
    Tense.FIRST_PERSON_CONDITIONAL_II_SINGULAR: lambda c: "bio bih " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.SECOND_PERSON_CONDITIONAL_II_SINGULAR: lambda c: "bio bi " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.THIRD_PERSON_CONDITIONAL_II_SINGULAR: lambda c: "bio bi " + c["app.ms"]
    if c.get("app.ms") is not None
    else None,
    Tense.FIRST_PERSON_CONDITIONAL_II_PLURAL: lambda c: "bili bismo " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.SECOND_PERSON_CONDITIONAL_II_PLURAL: lambda c: "bili biste " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.THIRD_PERSON_CONDITIONAL_II_PLURAL: lambda c: "bili bi " + c["app.mp"]
    if c.get("app.mp") is not None
    else None,
    Tense.FIRST_PERSON_IMPERATIVE_SINGULAR: lambda c: c.get("impt.2s"),
    Tense.FIRST_PERSON_IMPERATIVE_PLURAL: lambda c: c.get("impt.1p"),
    Tense.SECOND_PERSON_IMPERATIVE_PLURAL: lambda c: c.get("impt.2p"),
    # TODO Active past participle. Get advice from a linguist.
}


def build_tenses(tense_data: dict) -> dict[Tense, Optional[str]]:
    return {tense: builder(tense_data) for tense, builder in TENSE_BUILDERS.items()}


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
    "ē": "e",
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


def strip_links(string: str) -> str:
    return string.replace("[", "").replace("]", "")


def get_verb(entries: list[str]) -> Optional[str]:
    # (to \w+),?\s?
    # This is fully a wreck, but I'm trying to be quick and compact
    cleaned_entries = [
        # First sub drops semicolons nad periods, second drops stuff
        # inside parentheses. Strip to dump whitespace at ends
        re.sub(r"[;\.]", "", re.sub(r"\(.*\)", "", cleaned_value)).strip()
        for cleaned_value in filter(
            # Filter will drop empty string and null entries
            bool,
            [
                # This sub drops anything between sets of double braces {{}}
                # We also get rid of the little hash-space line starter
                re.sub(r"{{.*?}}", "", strip_links(entry.replace("# ", "")))
                for entry in entries
                if entry and entry.startswith("# ")
            ],
        )
    ]

    # Now we should have something like
    # ['to be, to exist', 'to equal, to total, to add up to',
    # 'there will be, there is going to be, to be coming']

    # Let's split and flatten, and filter for infinitives
    all_possibilities = [
        list_item
        for sublist in cleaned_entries
        for list_item in sublist.split(", ")
        if list_item.startswith("to")
    ]
    if len(all_possibilities) == 0:
        return None
    # After all that... just get the first one lol.
    return all_possibilities[0]


def clean_conjugation_entries(entries: list[str]) -> Optional[dict]:
    output = {}
    for entry in entries:
        if entry.startswith("|"):
            try:
                tense, conjugation = tuple(
                    strip_links(entry).replace("|", "").split("=")
                )
            except ValueError:
                print(
                    "Failed to clean conjugation section. Section isn't "
                    "in templated form."
                )
                return None
            if "<br" in conjugation:
                # NOTE I've only ever seen <br/>, <br> and <br />.
                # I think a bot does this automagically?
                split_term = ""
                if "<br />" in conjugation:
                    split_term = "<br />"
                elif "<br/>" in conjugation:
                    split_term = "<br/>"
                elif "<br>" in conjugation:
                    split_term = "<br>"
                else:
                    raise ValueError(f"Goofy line-break in conjugation: {conjugation}")

                possibilities = conjugation.split(split_term)
                if "impf" in conjugation:
                    # If we're deciding whether or not we should take the imperfect
                    # form or the perfect form, we'll take the imperfect form.
                    with_impf = list(
                        filter(
                            lambda e: "impf." in e and not "impf.," in e, possibilities
                        ),
                    )
                    if len(with_impf) != 1:
                        raise ValueError(
                            f"Goofy state for conjugation {conjugation}: "
                            f"resultant list is {with_impf}"
                        )
                    # Sample: " sam ''(impf.)''"
                    conjugation = with_impf[0].replace("''(impf.)''", "").strip()

                else:
                    # If it's just a split-line because you can say it either way,
                    # just take the first one.
                    if len(possibilities) < 2:
                        raise ValueError(
                            f"Goofy state for conjugation: {conjugation}: "
                            f"resultant list is {possibilities}"
                        )
                    conjugation = possibilities[0]
            new_conjugation = str()
            for character in conjugation:
                if character in GOOFY_CHARS:
                    new_conjugation += GOOFY_CHARS[character]
                else:
                    new_conjugation += character
            output[tense] = new_conjugation

    return output


def iterate_xml(xml_path: str) -> Iterator[dict]:
    context = ET.iterparse(xml_path, events=("start", "end"))
    conjugations_missing = 0
    verbs_missing = 0
    # For every element in the document,
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
            # Here is where things get interesting.
            text_lines = text.text.splitlines()
            verb_section = []
            verb_found = False
            conjugation_section = []
            conjugation_found = False
            # For every line of the article text,
            for index, line in enumerate(text_lines):
                # If we find a ==Serbo-Croatian== header, it's
                # time to stop and look around.
                if WIKTIONARY_SERBO_CROATIAN_HEADER.match(line) is not None:
                    # I could make these functions, but meh.
                    # Chomp this section until we find conjugations.
                    # Chomp the conjugations.
                    j = index
                    while True:
                        if (
                            # If we haven't found a conjugation for this verb yet,
                            # but we _do_ see a conjugation header,
                            not conjugation_found
                            and CONJUGATION_HEADER.match(text_lines[j]) is not None
                        ):
                            # Say we found it, for now.
                            conjugation_found = True
                            # Set an index based on the line we're at where we can
                            # see the header.
                            k = j + 1
                            while True:
                                # Starting at the line after the header, collect
                                # the current line if it ISN'T another section header.
                                if not WIKTIONARY_ANY_HEADER.match(text_lines[k]):
                                    conjugation_section.append(text_lines[k])
                                # If it IS another section header, it means that we're
                                # done collecting this section, and we need to break
                                # this loop.
                                else:
                                    break
                                # Alternatively, if the next line we look at would be
                                # past the page, we should _also_ break the loop. Otherwise
                                # we're wandering off into the no.
                                if k + 1 >= len(text_lines):
                                    break
                                # Finally, if we haven't broken out, then we still have
                                # more lines to collect for this section. Add to our index.
                                k += 1
                        # If we've run out of lines in the page,
                        # then we should stop scanning the page.
                        if j + 1 >= len(text_lines):
                            break
                        j += 1

                    # Now: If we found the conjugation section but we didn't wind up
                    # With any entries, something goofy happened and we should continue on.
                    if conjugation_found and not conjugation_section:
                        conjugation_found = False
                    # See the above loop for documentation on how this works.
                    # It's essentially the same with some different conditionals.
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

                    if verb_found and not verb_section:
                        verb_found = False

            if not conjugation_section:
                conjugation_found = False
                print(f"No conjugation section for {word}!")
                conjugations_missing += 1
                continue
            if not verb_section:
                verb_found = False
                print(f"No verb section for {word}!")
                verbs_missing += 1
                continue
            # Clean up the conjugation section.
            cleaned_conjugation_entries = clean_conjugation_entries(conjugation_section)
            # It's possible that we had a non-null conjugation section that just
            # didn't have anything interesting in it. After cleaning, we should
            # wind up with nothing.
            if not cleaned_conjugation_entries:
                print(f"No interesting conjugation entries for {word}!")
                conjugations_missing += 1
                continue
            tenses = build_tenses(tense_data=cleaned_conjugation_entries)
            english_verb = get_verb(entries=verb_section)
            if not english_verb:
                print(
                    f"Didn't find an english verb for {word}. Maybe it was an alternative form?"
                )
                verbs_missing += 1
                continue
            yield {
                "word": word,
                "english": english_verb,
                "conjugations": tenses,
            }

        root.clear()
    print(
        f"Got done formatting stuff. {conjugations_missing} verbs had missing "
        f"or broken conjugation sections. I also failed to deal with {verbs_missing} "
        "verbs -- I couldn't get an english translation for them. These numbers don't "
        "necessarily overlap 100%."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input-file", help="The XML file to read.", required=True
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="The JSON file to write.",
        required=False,
        default="output.json",
    )
    args = parser.parse_args()
    with open(args.output_file, "w") as file_handle:
        output = {
            entry["word"]: entry
            for entry in sorted(
                [word for word in iterate_xml(xml_path=args.input_file)],
                key=lambda e: e["word"],
            )
        }
        json.dump(
            output,
            file_handle,
            ensure_ascii=False,
        )
        print(f"Wrote to {args.output_file}...")


if __name__ == "__main__":
    main()
