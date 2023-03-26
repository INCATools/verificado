import pandas as pd

from oaklib.implementations.ubergraph import UbergraphImplementation

from .utils.utils import get_config, verify_relationship, split_terms

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
  
def validate(config, filename):
  config = get_config(config)
  data = pd.read_csv(config["pairs_filename"])
  terms_pairs = get_pairs(data)
  prefixes = get_prefixes(config["ontologies"])

  for _, rel in config["relationships"].items():
    _, terms_pairs = verify_relationship(query_ubergraph, prefixes, terms_pairs, rel)
  
  terms_s, terms_o = split_terms(terms_pairs)

  rows_nv = data[data[["s","o"]].apply(tuple, 1).isin(zip(terms_s, terms_o))]
  
  rows_nv.to_csv(filename, index=False)

