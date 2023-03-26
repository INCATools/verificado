import os
import logging
from ruamel.yaml import YAML, YAMLError

QUERY = """
   VALUES (?subject ?object) {{
      {pairs}
    }}
    ?subject {property} ?object .
"""

def chunks(lst, n):
  for i in range(0, len(lst), n):
      yield lst[i:i + n]

def transform_to_str(list):
  terms_pairs = set()

  for s, o in list:
    terms_pairs.add(f"({s} {o})")
  return terms_pairs

def split_terms(list):
  terms_s = []
  terms_o = []

  for pairs in list:
    s, o = pairs.split(" ")
    terms_s.append(s[1:])
    terms_o.append(o[:-1])

  return terms_s, terms_o

def extract_results(list):
  return set((r["subject"], r["object"]) for r in list)


def verify_relationship(query_ubergraph, prefixes, terms_pairs, relationship):
  valid_relationship = set()
  if len(terms_pairs) > 90:
    for chunk in chunks(list(terms_pairs), 90):
      valid_relationship = valid_relationship.union(extract_results(query_ubergraph(QUERY.format(pairs=" ".join(chunk), property=relationship), prefixes)))
  else:
    valid_relationship = extract_results(query_ubergraph(QUERY.format(pairs=" ".join(list(terms_pairs)), property=relationship), prefixes))
  
  non_valid_relationship = terms_pairs - transform_to_str(valid_relationship)

  return valid_relationship, non_valid_relationship


def get_config(input) -> dict:
  if input.endswith('.yaml') or input.endswith('.yml'):
    config = os.path.abspath(input)
    ryaml = YAML(typ='safe')
    with open(config, "r") as f:
      try:
        config = ryaml.load(f)
      except YAMLError as exc:
        logging.info(f'Failed to load config: {config}')
    return config
  else:
    logging.error("Given path has unsupported file extension.")
    return False
  