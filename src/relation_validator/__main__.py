"""
Command-line application for the lib
"""
import argparse
import pathlib

from .validator import ontologies_version, validate


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help="Available relation-validator actions",
    )

    parser_validate = subparsers.add_parser(
        name="validate",
        description="The validate parser",
        help="Validates the pairs using the relationships in the input file"
    )
    parser_validate.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        required=True,
        help="yaml file with config"
    )
    parser_validate.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        required=True,
        help="csv output filename"
    )
    parser_validate.set_defaults(func=validate)

    parser_ont_versions = subparsers.add_parser(
        name="ontologies_version",
        add_help=True,
        help="Ontologies' version available in Ubergraph"
    )
    parser_ont_versions.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        required=True,
        help="json output filename"
    )
    parser_ont_versions.set_defaults(func=ontologies_version)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
