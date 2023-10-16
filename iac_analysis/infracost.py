import yaml
from typing import Dict, Any, Callable


def read_usage_yaml(fpath: str) -> Dict[str, Any]:
    with open(fpath, "r") as f:
        return yaml.safe_load(f)


def metric_usage_with_callback(
    infracost_usage: Dict[str, Any],
    address: str,
    resource_type: str,
    metric: str,
    callback: Callable[[int], None],
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
