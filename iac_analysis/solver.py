import z3
from z3 import parse_smt2_string, parse_smt2_file, sat, unsat, unknown
import logging

logger = logging.getLogger(__name__)


class Solver:
    def __init__(self):
        self.pool = {}
        self.constraints = []
        self._solver = z3.Solver()

    def nv(self, resource, metric):
        varname = f"{resource.name}.{metric}"
        if not varname in self.pool:
            self.pool[varname] = z3.Int(varname)
        return self.pool[varname]

    def existing_nv(self, resource, metric):
        varname = f"{resource.name}.{metric}"
        if varname in self.pool:
            return self.pool[varname]
        return None

    def ev(self, source, destination, metric):
        varname = f"{source.name}_{destination.name}.{metric}"
        if not varname in self.pool:
            self.pool[varname] = z3.Int(varname)
        return self.pool[varname]

    def existing_ev(self, source, destination, metric):
        varname = f"{source.name}_{destination.name}.{metric}"
        if varname in self.pool:
            return self.pool[varname]
        return None

    def add(self, constraint):
        self.constraints.append(constraint)
        self._solver.add(constraint)

    def add_aggregate_incoming_constraint(self, x, metric):
        incoming = [
            x
            for x in [self.existing_ev(inn, x, metric) for inn in x.incoming_edges]
            if not x is None
        ]
        if len(incoming) > 0:
            self.add(self.nv(x, metric) == sum(incoming[1:], incoming[0]))

    def add_estimates(self, all_resources, estimates):
        for resource_name, metrics in estimates.items():
            if not resource_name in all_resources:
                logger.error(f"{resource_name} does not exist in the infrastructure")
            resource = all_resources[resource_name]
            for metric, estimate in metrics.items():
                self.add(self.nv(resource, metric) == estimate)

    def check(self):
        return self._solver.check()

    def sexpr(self):
        return self._solver.sexpr()
