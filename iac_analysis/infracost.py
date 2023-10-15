import yaml
from typing import Dict, Any


def read_usage_yaml(fpath: str) -> Dict[str, Any]:
    with open(fpath, "r") as f:
        return yaml.safe_load(f)


def metric_usage_with_callback(
    infracost_usage, address, resource_type, metric, callback
):
    try:
        callback(infracost_usage["resource_usage"][address][metric])
    except KeyError:
        try:
            callback(
                infracost_usage["resource_type_default_usage"][resource_type][metric]
            )
        except KeyError:
            pass
