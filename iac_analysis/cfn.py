from iac_analysis import infra
import yaml
from graphlib import TopologicalSorter


def load_template(fpath: str):
    # TODO: Support JSON
    with open(fpath, "r") as f:
        return yaml.safe_load(f)
