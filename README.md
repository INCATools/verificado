# Relationship validator

Validation process using [Ubergraph](https://zenodo.org/record/7249759#.ZDRuZOzML1c) as source of truth.

Ubergraph is an RDF triplestore with [39 OBO ontologies](https://github.com/INCATools/ubergraph#integrated-obo-ontology-triplestore) merged, precomputed OWL classification and materialized class relationship from existential properties restriction.


## Install

```bash
pip install relation-validator
```

## Configure YAML file

In the config file, it is defined the list of relationships the validation should run on. The order is essential.

The yaml file needs to have the keys `relationships` and `filename`. Check an example below:

```yaml
relationships:
  sub_class_of: rdfs:subClassOf
  part_of: BFO:0000050
  connected_to: RO:0001025
  has_soma_location: RO:0002100
  ...

filename: path/to/filename.csv
```

The filename should have the following columns:

| s                   | slabel                                | user_slabel                               | o                  | olabel                                | user_olabel                               |
|---------------------|---------------------------------------|-------------------------------------------|--------------------|---------------------------------------|-------------------------------------------|
| the subject term ID | the label of the term in the column s | optional label for the term given by user | the object term ID | the label of the term in the column s | optional label for the term given by user |

## Run relation-validator CLI

```bash
relation-validator validate --input path/to/config.yaml --output path/to/output.csv
```

The `output.csv` file will be in the same format as the `filename.csv`. It will return the cases where a triple (subject, relationship, object) with the relationships listed in the yaml file was not found in Ubergraph.

## List of ontologies available

To know which ontologies and their version are available in Ubergraph, use the following CLI:

```bash
relation-validator ontologies_version --output filename.json
```