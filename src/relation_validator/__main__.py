import argparse
import pathlib

from .validator import ontologies_version, validate


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        help='Available dosdp actions',
        dest='action'
    )

    parser_validate = subparsers.add_parser(
        name="validate",
        description="The validate parser",
        help="Validates the pairs using the relationships in the input file"
    )
    parser_validate.add_argument(
        name_or_flags="-i",
        name_or_flags="--input",
        action="store",
        type=pathlib.Path,
        required=True,
        help="yaml file with config"
    )
    parser_validate.add_argument(
        name_or_flags="-o",
        name_or_flags="--output",
        action="store",
        type=pathlib.Path,
        required=True,
        help="csv output filename"
    )

    parser_ont_versions = subparsers.add_parser(
        name="ontologies_version",
        add_help=True,
        help="Ontologies' version available in Ubergraph"
    )
    parser_ont_versions.add_argument(
        name_or_flags="-o",
        name_or_flags="--output",
        action="store",
        type=pathlib.Path,
        required=True,
        help="json output filename"
    )

    args = parser.parse_args()

    if args.action == "validate":
        validate(str(args.input), str(args.output))
    elif args.action == "ontologies_version":
        ontologies_version(args.output)


if __name__ == "__main__":
    main()
