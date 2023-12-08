import iac_analysis.cfn as cfn
from iac_analysis.resource import (
    Resource,
    supported_resource_types,
    ignore_resource_types,
)
import logging
import graphlib

logger = logging.getLogger(__name__)


class Infra:
    def __init__(self, resources):
        self.resources = resources
        for _, r in self.resources.items():
            r.compute_edges(self.resources)
        # TODO: topological sort here first
        ts = graphlib.TopologicalSorter()
        for _, r in self.resources.items():
            ts.add(r, *r.incoming_edges)
        self.topologically_sorted_resources = [*ts.static_order()]

    @classmethod
    def from_template(cls, fpath):
        c = cfn.load_template(fpath)
        resources = {}
        for name, body in c["Resources"].items():
            resource_type = body["Type"]
            if resource_type in supported_resource_types:
                r = Resource(name, resource_type, body)
                resources[name] = r
            elif resource_type not in ignore_resource_types:
                logger.warning(f"Unsupported resource type: {resource_type}")

        return cls(resources)

    def print_edges(self):
        for r in self.topologically_sorted_resources:
            print(f"Edges at {r.name}:")
            for incoming_r in r.incoming_edges:
                print(f"incoming --> {incoming_r.name}")
            for outgoing_r in r.outgoing_edges:
                print(f"outgoing <-- {outgoing_r.name}")

    def compute_constraints(self, solver):
        for r in self.topologically_sorted_resources:
            r.compute_constraints(solver)
