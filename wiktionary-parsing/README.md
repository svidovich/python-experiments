# Wiktionary Parsing

So turns out I suck at conugating verbs. That's fine, somebody doesn't, and they put a bunch of them on Wiktionary. Here's what we did to process all of them.

So download all of wiktionary here: [Wiktionary Latest Folder](https://dumps.wikimedia.org/enwiktionary/latest/)

They're bzip'd XML documents. The one I used is called `enwiktionary-latest-pages-articles.xml.bz2`. It was about 1.1G packed, and 8.3G unpacked.

You can extract it with `7z x`.

So then I went and found all of the Serbo-Croatian verbs. You can see them here: [link](https://en.wiktionary.org/wiki/Category:Serbo-Croatian_verbs). I got all of the ones in latin text, and put them in a newline delimited document. It looked like

```
abaiti
abdicirati
abecedirati
ablendati
abonirati
abortirati
abrogirati
abundati
adaptirati
adjustirati
adoptirati
adorati
adorirati
...
```

Which was cool. I wanted to pare down the entirety of Wiktionary to _just the pages I cared about_, so I wrote `pare.py`, which takes the wordlist and the xml and cuts it down.

```shell
usage: pare.py [-h] -w WORD_LIST_FILE -x WIKTIONARY_XML_FILE [-o OUTPUT_FILE]

Given a file containing a list of "words of interest" and a Wiktionary XML, pare the XML down to only
the pages that match our words of interest, and save it off to a new location.

options:
  -h, --help            show this help message and exit
  -w WORD_LIST_FILE, --word-list-file WORD_LIST_FILE
                        Path to a newline-delimited list of words to be looked up.
  -x WIKTIONARY_XML_FILE, --wiktionary-xml-file WIKTIONARY_XML_FILE
                        Path to a wiktionary XML file.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Where to write the filtered XML
```

tl;dr

```shell
python3 pare.py -w all-verbs-list.txt -x ~/.../enwiktionary-latest-pages-articles.xml -o filteredwiki.xml
```

This generates an XML file that lookslike this:

```xml
<parent xmlns:ns0="http://www.mediawiki.org/xml/export-0.10/"><pagecontainer><ns0:page>
    <ns0:title>je</ns0:title>
    <ns0:ns>0</ns0:ns>
    <ns0:id>37650</ns0:id>
    <ns0:revision>
      <ns0:id>76257874</ns0:id>
      <ns0:parentid>75946569</ns0:parentid>
      <ns0:timestamp>2023-10-03T11:41:46Z</ns0:timestamp>
      <ns0:contributor>
        <ns0:username>Appolodorus1</ns0:username>
        <ns0:id>3705051</ns0:id>
      </ns0:contributor>
      <ns0:comment>/* Pronoun */</ns0:comment>
      <ns0:model>wikitext</ns0:model>
      <ns0:format>text/x-wiki</ns0:format>
      <ns0:text bytes="16751" xml:space="preserve">{{also|Appendix:Variations of "je"}}
==Albanian==
```

Lmao albanian. Anyway, there's a parent element and each page has its own `<pagecontainer>`.

The filtered XML is about 9.2M, which is _way more workable_.

Next, I needed to parse that into a usable blob of JSON, so I wrote `collect_words.py`.

```shell
usage: collect_words.py [-h] -i INPUT_FILE [-o OUTPUT_FILE]

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        The XML file to read.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The JSON file to write.
```

This takes your pared down XML output from `pare.py` and barfs up JSON of the form

```json
{
  "abdicirati": {
    "word": "abdicirati",
    "english": "to abdicate",
    "conjugations": {
      "first_person_present_singular": "abdiciram",
      "second_person_present_singular": "abdiciraš",
      "third_person_present_singular": "abdicira",
      "first_person_present_plural": "abdiciramo",
      "second_person_present_plural": "abdicirate", ...
    }, ...
  }, ...
}

```

but with all of the tenses you know and love. There are a couple particulars to discuss.

- Some verbs come with multiple forms in their conjugation, like impf. and pf. We always take the impf there. Maybe that's wrong.
- We skipped verbs that missed conjugation sections.
- We skipped verbs without an available english translation.
- We built the conjugations based on Wiktionary's templating, see [link](https://en.wiktionary.org/wiki/Template:sh-conj).
- Some verbs come with multiple options, like `bȉjāh / bjȅh / bȅjāh / bȅh`. We take the first option.
- Oh yeah, we ditch those fancy characters, too.

Now we want to turn it into a CSV, so we wrote `mkcsv.py` that takes the output of `collect_words.py` and makes a nice flat CSV.

```shell
usage: mkcsv.py [-h] -i INPUT_FILE [-o OUTPUT_FILE]

CSV-ify the results from collect_words.py.

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        Input JSON document
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output CSV file
```

The results are in `output.csv` in the repo, since they were small enough to commit.
