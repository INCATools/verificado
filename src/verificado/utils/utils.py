"""
Script with util function used in validator
"""
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from oaklib.datamodels.obograph import Edge, Graph, Node
from oaklib.implementations.ubergraph import UbergraphImplementation
from oaklib.utilities.obograph_utils import graph_to_image
from pandas import DataFrame
from ruamel.yaml import YAML, YAMLError

from verificado import conf as conf_package

QUERY = """
    VALUES (?subject ?object) {{
        {pairs}
    }}
    ?subject {property} ?object .
    # LIMIT
"""

QUERY_LABEL = """
    VALUES (?subject) {{
        {terms}
    }}
    ?subject rdfs:label ?object .
    # LIMIT
"""

DEFAULT_STYLE = "obograph-style.json"


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


def transform_to_str(entry: List[set]) -> set:
    """
    Transform the pairs in the list into string in the format "(s, o)"
    """
    terms_pairs = set()

    for s, o in entry:
        terms_pairs.add(f"({s} {o})")

    return terms_pairs


def split_terms(entry: List[str]) -> (List[str], List[str]):
    """
    Return s and o terms
    """
    terms_s = []
    terms_o = []

    for pairs in entry:
        s, o = pairs.split(" ")
        terms_s.append(s[1:])
        terms_o.append(o[:-1])

    return (terms_s, terms_o)


def extract_results(entry: List[dict]) -> set:
    """
    Extract values subject and object from result
    """
    return set((r["subject"], r["object"]) for r in entry)


def verify_relationship(
    terms_pairs: List[str],
    relationship: str
) -> (set, set):
    """
    Query Ubergraph with term pairs and relationship.
    Return valid and not valid pairs.
    """
    valid_relationship = set()

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

    non_valid_relationship = set(
        terms_pairs - transform_to_str(valid_relationship)
    )

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


def get_obograph(
    rel_terms: Dict[str, List[Tuple[str, str]]],
    labels: Dict[str, str],
    properties: Dict[str, str]
) -> Graph:
    """
    Transform graph into OBOGgraph
    """
    edges = []
    nodes = {}
    properties_ = {v: k for k, v in properties.items()}

    for rel, terms in rel_terms.items():
        for sub, obj in terms:
            edges.append(Edge(sub=sub, pred=rel, obj=obj))
            nodes[sub] = Node(id=sub, lbl=labels[sub])
            nodes[obj] = Node(id=obj, lbl=labels[obj])
            if "not_matched" not in rel:
                nodes[rel] = Node(id=rel, lbl=properties_[rel])

    return Graph(id="valid", nodes=list(nodes.values()), edges=edges)


def save_obograph(
    graph: Graph,
    output: Path,
    stylegraph: Optional[str] = None
):
    """
    Save OBOGraph in image
    """
    if stylegraph is None:
        conf_path = os.path.dirname(conf_package.__file__)
        stylegraph = str(Path(conf_path) / DEFAULT_STYLE)
    graph_to_image(graph=graph, imgfile=output, stylemap=stylegraph)


def to_set(term_pairs: Set[str]) -> Set[Tuple[str, str]]:
    """
    Transform set of strings into set of tuples
    """
    res = set()
    for pair in term_pairs:
        term_s, term_o = split_terms([pair])
        res.add((term_s[0], term_o[0]))
    return res


def get_labels(data: DataFrame) -> Dict[str, str]:
    """
    Get labels from terms in table or search for missing labels in Ubergraph
    """
    labels = {}
    terms = set()
    for _, row in data.iterrows():
        if row["s"] not in labels:
            if row["slabel"] != "":
                labels[row["s"]] = row["slabel"]
            else:
                terms.add(f"({row['s']})")
        if row["o"] not in labels:
            if row["olabel"] != "":
                labels[row["o"]] = row["olabel"]
            else:
                terms.add(f"({row['o']})")

    ont_labels = search_labels(terms)
    for term, label in ont_labels:
        labels[term] = label

    return labels


def tsv_or_csv(filename: Path) -> tuple[str, str]:
    """
    Extract file extension to give proper sep for loading TSV or CSV table
    """
    temp_filename, extension = os.path.splitext(filename)

    # DEFAULT TO CSV
    sep = ","
    if "tsv" in extension:
        sep = "\t"

    return temp_filename, sep, extension


def save_tsv_or_csv(data: DataFrame, filename: str):
    """
    Save DataFrame with file proprer TSV or CSV extension
    """
    if str(filename).endswith(".csv"):
        sep = ','
    elif str(filename).endswith(".tsv"):
        sep = '\t'
    else:
        raise ValueError("Unsupported file extension. Please provide a .csv or .tsv file.")
    data.to_csv(filename, sep=sep, index=False)


def parse_table(data: DataFrame) -> DataFrame:
    """
    Parse generic tree table to pairs table
    """
    terms = {}
    # Generate dict with terms and label
    for _, row in data.iterrows():
        for term_id, label in chunks(data.columns, 2):
            terms[row.loc[term_id]] = row.loc[label]

    table_parsed = []
    for _, row in data.filter(regex=".*ID").iterrows():
        for current, next in zip(row, row[1:]):
            r = {}
            r['s'] = next
            r['slabel'] = ""
            r['user_slabel'] = terms[next]
            r['o'] = current
            r['olabel'] = ""
            r['user_olabel'] = terms[current]
            table_parsed.append(r)

    return DataFrame.from_records(table_parsed).drop_duplicates()


def search_labels(terms: set) -> set:
    """
    Search label for terms in Ubergraph
    """
    result = set()
    for chunk in chunks(list(terms), 90):
        result = result.union(
            extract_results(
                query_ubergraph(
                    QUERY_LABEL.format(
                        terms=" ".join(chunk)
                    )
                )
            )
        )
    return result
