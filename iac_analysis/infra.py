import iac_analysis.cfn as cfn
from iac_analysis.resource import (
    Resource,
    supported_resource_types,
    ignore_resource_types,
    public_usage_metrics,
    metrics,
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
        # INFO: we can actually allow cyclic graphs and they can be useful
        # if not nx.is_directed_acyclic_graph(self.graph):
        #     logger.error("Graph is cyclic.")

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

    def compute_constraints(self, solver, custom_generator=None):
        # instantiate the solver variables and basic constraints
        for _, r in self.resources.items():
            for metric in metrics[r.resource_type]:
                solver.add(solver.nv(r, metric) >= 0)
                # TODO: this is true given the current supported metrics but might not be true for all edge variables
                # At that point, should probably put this in the resource's compute_constraints function
                for inn in r.incoming_edges:
                    solver.add(solver.ev(inn, r, metric) >= 0)

        # compute constraints in topological order
        # topological order is needed for computing the incoming constraints
        for _, r in self.resources.items():
            r.compute_constraints(
                solver, self.resources, custom_generator=custom_generator
            )

    def draw(self, fname):
        nx.draw(self.graph, with_labels=True)
        plt.savefig(fname)
        plt.clf()

    def average_degree(self):
        return 2 * self.graph.number_of_edges() / float(self.graph.number_of_nodes())
