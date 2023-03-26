import argparse
import pathlib

from .validator import validate

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', type=pathlib.Path, required=True, help="yaml file with config")
  parser.add_argument('-o', '--output', type=pathlib.Path, required=True, help="output filename")

  args = parser.parse_args()

  validate(str(args.input), str(args.output))

if __name__ == "__main__":
  main()