import yaml
from iac_analysis.resource import public_usage_metrics


def load_estimates(fpath):
    with open(fpath, "r") as f:
        return yaml.safe_load(f)


def generate_estimates_template(infra):
    template = {}
    for _, r in infra.resources.items():
        if r.resource_type in public_usage_metrics:
            r_template = {}
            for m in public_usage_metrics[r.resource_type]:
                r_template[m] = 0
            template[r.name] = r_template
    return template
