"""
mkcsv.py

CSV-ify the results from collect_words.py.
"""
# pylint: disable=unspecified-encoding,missing-function-docstring

import argparse
import json
import csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CSV-ify the results from collect_words.py."
    )
    parser.add_argument("-i", "--input-file", required=True, help="Input JSON document")
    parser.add_argument(
        "-o",
        "--output-file",
        required=False,
        default="output.csv",
        help="Output CSV file",
    )
    args = parser.parse_args()

    with open(args.input_file) as file_handle:
        data: dict[str, dict] = json.load(file_handle)

    tenses = list(next(iter(data.values()))["conjugations"].keys())

    fieldnames = ["word", "english", *tenses]

    with open(args.output_file, "w") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data.values():
            writer.writerow(
                {
                    "word": entry["word"],
                    "english": entry["english"],
                    **entry["conjugations"],
                }
            )
        print(f"OK, wrote to {args.output_file}")


if __name__ == "__main__":
    main()
