"""
Script with util function used in validator
"""
import logging
import os

from oaklib.implementations.ubergraph import UbergraphImplementation
from ruamel.yaml import YAML, YAMLError

QUERY = """
    VALUES (?subject ?object) {{
        {pairs}
    }}
    ?subject {property} ?object .
    # LIMIT
"""


def query_ubergraph(query):
    """
    Query Ubergraph and return results
    """
    oi = UbergraphImplementation()
    prefixes = get_prefixes(query, oi.prefix_map().keys())

    res = oi.query(query=query, prefixes=prefixes)

    return list(res)


def get_pairs(data):
    """
    Get pairs (s, o) from DataFrame
    """
    pairs = set()
    for _, row in data.iterrows():
        pairs.add(f"({row['s']} {row['o']})")
    return pairs


def chunks(lst, n):
    """
    Chunk funtion
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def transform_to_str(entry: list):
    """
    Transform the pairs in the list into string in the format "(s, o)"
    """
    terms_pairs = set()

    for s, o in entry:
        terms_pairs.add(f"({s} {o})")

    return terms_pairs


def split_terms(entry: list) -> (list, list):
    """
    Return s and o terms
    """
    terms_s = []
    terms_o = []

    for pairs in entry:
        s, o = pairs.split(" ")
        terms_s.append(s[1:])
        terms_o.append(o[:-1])

    return terms_s, terms_o


def extract_results(entry: list):
    """
    Extract values subject and object from result
    """
    return set((r["subject"], r["object"]) for r in entry)


def verify_relationship(terms_pairs, relationship):
    """
    Query Ubergraph with term pairs and relationship.
    Return valid and not valid pairs.
    """
    valid_relationship = set()
    if len(terms_pairs) > 90:
        for chunk in chunks(list(terms_pairs), 90):
            valid_relationship = valid_relationship.union(
                extract_results(
                    query_ubergraph(
                        QUERY.format(
                            pairs=" ".join(chunk), property=relationship
                        )
                    )
                )
            )
    else:
        valid_relationship = extract_results(
            query_ubergraph(
                QUERY.format(
                    pairs=" ".join(list(terms_pairs)),
                    property=relationship
                )
            )
        )

    non_valid_relationship = terms_pairs - transform_to_str(valid_relationship)

    return valid_relationship, non_valid_relationship


def get_config(entry) -> dict:
    """
    Parse config file
    """
    if entry.suffix not in (".yaml" or ".yml"):
        logging.error("Given path has unsupported file extension.")
        return {}

    config = os.path.abspath(entry)
    ryaml = YAML(typ="safe")
    with open(config, "r", encoding="utf-8") as f:
        try:
            config = ryaml.load(f)
        except YAMLError:
            logging.info("Failed to load config: %s", config)
    return config


def get_prefixes(text, prefix_map):
    """
    Filter prefix only on the pair terms
    """
    prefixes = []
    for prefix in prefix_map:
        if prefix in text:
            prefixes.append(prefix)

    return prefixes


def get_ontologies_version():
    """
    Query Ubergraph all ontology and its version
    """
    QUERY_VERSION = """
        ?ontology a owl:Ontology .
        OPTIONAL { ?ontology owl:versionIRI ?version . }
        # LIMIT
    """

    response = query_ubergraph(QUERY_VERSION)
    return response
