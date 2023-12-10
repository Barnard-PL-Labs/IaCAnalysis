import iac_analysis.cfn as cfn
from iac_analysis.resource import (
    Resource,
    supported_resource_types,
    ignore_resource_types,
    public_usage_metrics,
)
import logging
import networkx as nx
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class Infra:
    def __init__(self, resources):
        self.resources = resources
        # compute edges for all resources
        for _, r in self.resources.items():
            r.compute_edges(self.resources)
        # create directed graph for infrastructure
        self.graph = nx.DiGraph()
        for _, r in self.resources.items():
            self.graph.add_node(r)
            for inn in r.incoming_edges:
                self.graph.add_edge(inn, r)
        if not nx.is_directed_acyclic_graph(self.graph):
            logger.error("Graph is cyclic.")

    @classmethod
    def from_cfn(cls, fpath):
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
        for _, r in self.resources.items():
            print(f"Edges at {r.name}:")
            for incoming_r in r.incoming_edges:
                print(f"incoming --> {incoming_r.name}")
            for outgoing_r in r.outgoing_edges:
                print(f"outgoing <-- {outgoing_r.name}")

    def compute_constraints(self, solver):
        # compute constraints in topological order
        # topological order is needed for computing the incoming constraints
        for r in nx.topological_sort(self.graph):
            r.compute_constraints(solver, self.resources)

    def draw(self, fname):
        nx.draw(self.graph, with_labels=True)
        plt.savefig(fname)
        plt.clf()
