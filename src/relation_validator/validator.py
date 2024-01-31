"""
Validator script
"""
import json
import os
from typing import Dict, List, Tuple

import pandas as pd

from .utils.utils import (get_config, get_labels, get_obograph,
                          get_ontologies_version, get_pairs, save_obograph,
                          split_terms, to_set, verify_relationship)


def run_validation(
    data: pd.DataFrame,
    relationships: dict
) -> (pd.DataFrame, Dict[str, List[Tuple[str, str]]]):
    """
    Validation process for each relationship
    """
    terms_pairs = get_pairs(data)
    rel_terms = {}
    for _, rel in relationships.items():
        valid_terms, terms_pairs = verify_relationship(terms_pairs, rel)
        if valid_terms:
            rel_terms[rel] = valid_terms

    rel_terms["not_matched"] = to_set(terms_pairs)

    terms_s, terms_o = split_terms(terms_pairs)

    rows_nv = data[
        data[["s", "o"]].apply(tuple, 1).isin(zip(terms_s, terms_o))
    ]

    return rows_nv, rel_terms


def validate(args):
    """
    Validate process
    """
    config = get_config(args.input)
    if not config:
        return exit

    data = pd.read_csv(config["filename"])

    temp_filename, _ = os.path.splitext(config["filename"])

    report, rel_terms = run_validation(data, config["relationships"])

    report.to_csv(args.output, index=False)

    labels = get_labels(data)
    graph = get_obograph(rel_terms, labels)
    save_obograph(graph, f"{temp_filename}.png")
    return True


def ontologies_version(args):
    """
    Get ontologies' version
    """
    ont_version = get_ontologies_version()
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(ont_version, f, ensure_ascii=False, indent=2)
