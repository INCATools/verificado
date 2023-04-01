import pandas as pd
import json

from .utils.utils import (
    get_config, 
    verify_relationship, 
    split_terms, 
    get_pairs,
    get_ontologies_version
)

def validate(config, filename):
  config = get_config(config)
  data = pd.read_csv(config["filename"])
  terms_pairs = get_pairs(data)

  for _, rel in config["relationships"].items():
    _, terms_pairs = verify_relationship(terms_pairs, rel)
  
  terms_s, terms_o = split_terms(terms_pairs)

  rows_nv = data[data[["s","o"]].apply(tuple, 1).isin(zip(terms_s, terms_o))]
  
  rows_nv.to_csv(filename, index=False)

def ontologies_version(filename):
  ont_version = get_ontologies_version()
  with open(filename, 'w', encoding='utf-8') as f:
    json.dump(ont_version, f, ensure_ascii=False, indent=2)
