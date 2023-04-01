import argparse
import pathlib

from .validator import validate
from .validator import ontologies_version

def main():
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(help='Available dosdp actions', dest='action')

  parser_validate = subparsers.add_parser("validate",
                                          description="The validate parser",
                                          help="Validates the pairs in filename using the relationships in the input file")
  parser_validate.add_argument('-i', '--input', action='store', 
                               type=pathlib.Path, required=True, 
                               help="yaml file with config")
  parser_validate.add_argument('-o', '--output', action='store', 
                               type=pathlib.Path, required=True, 
                               help="csv output filename")

  parser_ont_versions = subparsers.add_parser("ontologies_version", add_help=True,
                                              help="Ontologies' version available in Ubergraph")
  parser_ont_versions.add_argument('-o', '--output', action='store', 
                                   type=pathlib.Path, required=True, help="json output filename")
  
  args = parser.parse_args()

  if args.action == "validate":
    validate(str(args.input), str(args.output))
  elif args.action == "ontologies_version":
    ontologies_version(args.output)

if __name__ == "__main__":
  main()