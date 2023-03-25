import argparse
import pathlib
import pandas as pd

from oaklib.implementations.ubergraph import UbergraphImplementation

from utils import get_config, verify_relationship, split_terms


def query_ubergraph(query, prefixes):
  oi = UbergraphImplementation()
  
  res = oi.query(query=query, prefixes=prefixes)
  
  return [r for r in res]

def get_pairs(data):
  pairs = set()
  for _, row in data.iterrows():
    pairs.add(f"({row['s']} {row['o']})")
  return pairs

def get_prefixes(data):
  return [ont["id"] for ont in data]
  
def main(config, filename):
  config = get_config(config)
  data = pd.read_csv(config["pairs_filename"])
  terms_pairs = get_pairs(data)
  prefixes = get_prefixes(config["ontologies"])

  for _, rel in config["relationships"].items():
    _, terms_pairs = verify_relationship(query_ubergraph, prefixes, terms_pairs, rel)
  
  terms_s, terms_o = split_terms(terms_pairs)

  rows_nv = data[data[["s","o"]].apply(tuple, 1).isin(zip(terms_s, terms_o))]
  
  rows_nv.to_csv(filename, index=False)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', type=pathlib.Path, required=True, help="yaml file with config")
  parser.add_argument('-o', '--output', type=pathlib.Path, required=True, help="output filename")

  args = parser.parse_args()
  main(str(args.input), str(args.output))