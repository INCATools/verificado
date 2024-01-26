import json

import pandas as pd

from .utils.utils import (get_config, get_ontologies_version, get_pairs,
                          split_terms, verify_relationship)


def run_validation(data: pd.DataFrame, relationships: dict) -> pd.DataFrame:
    """
    Validation process for each relationship
    """
    terms_pairs = get_pairs(data)

    for _, rel in relationships.items():
        _, terms_pairs = verify_relationship(terms_pairs, rel)

    terms_s, terms_o = split_terms(terms_pairs)

    rows_nv = data[
        data[["s", "o"]].apply(tuple, 1).isin(zip(terms_s, terms_o))
    ]

    return rows_nv


def validate(args):
    """
    Validate process
    """
    config = get_config(args.input)
    if not config:
        return exit

    data = pd.read_csv(config["filename"])

    report = run_validation(data, config["relationships"])

    report.to_csv(args.output, index=False)


def ontologies_version(args):
    """
    Get ontologies' version
    """
    ont_version = get_ontologies_version()
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(ont_version, f, ensure_ascii=False, indent=2)
