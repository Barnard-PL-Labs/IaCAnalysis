import os
import z3
from z3 import parse_smt2_string, parse_smt2_file, sat, unsat, unknown, Implies
import logging

logger = logging.getLogger(__name__)


class Solver:
    def __init__(self):
        self.number_of_basic = 0
        self.number_of_intrinsic = 0
        self.number_of_incoming = 0
        self.number_of_outgoing = 0
        self.number_of_custom = 0
        self.number_of_estimate = 0
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

    def add_basic(self, constraint):
        if isinstance(constraint, z3.z3.AstVector):
            for c in constraint:
                self._add(c, "basic")
        else:
            self._add(constraint, "basic")

    def add_intrinsic(self, constraint):
        if isinstance(constraint, z3.z3.AstVector):
            for c in constraint:
                self._add(c, "intrinsic")
        else:
            self._add(constraint, "intrinsic")

    def add_incoming(self, constraint):
        if isinstance(constraint, z3.z3.AstVector):
            for c in constraint:
                self._add(c, "incoming")
        else:
            self._add(constraint, "incoming")

    def add_outgoing(self, constraint):
        if isinstance(constraint, z3.z3.AstVector):
            for c in constraint:
                self._add(c, "outgoing")
        else:
            self._add(constraint, "outgoing")

    def add_custom(self, constraint):
        if isinstance(constraint, z3.z3.AstVector):
            for c in constraint:
                self._add(c, "custom")
        else:
            self._add(constraint, "custom")

    def add_estimate(self, constraint):
        if isinstance(constraint, z3.z3.AstVector):
            for c in constraint:
                self._add(c, "estimate")
        else:
            self._add(constraint, "estimate")

    def _add(self, constraint, t):
        match t:
            case "basic":
                self.number_of_basic += 1
            case "intrinsic":
                self.number_of_intrinsic += 1
            case "incoming":
                self.number_of_incoming += 1
            case "outgoing":
                self.number_of_outgoing += 1
            case "custom":
                self.number_of_custom += 1
            case "estimate":
                self.number_of_estimate += 1
            case unknown_t:
                os.exit(f"BUG: unknown constraint type {unknown_t}")
        self.constraints.append(constraint)
        self._solver.add(constraint)

    def add_aggregate_incoming_constraint(self, x, metric):
        incoming = [
            x
            for x in [self.existing_ev(inn, x, metric) for inn in x.incoming_edges]
            if not x is None
        ]
        if len(incoming) > 0:
            self.add_incoming(self.nv(x, metric) == sum(incoming[1:], incoming[0]))

    def add_estimates(self, all_resources, estimates):
        for resource_name, metrics in estimates.items():
            if not resource_name in all_resources:
                logger.error(f"{resource_name} does not exist in the infrastructure")
            resource = all_resources[resource_name]
            for metric, estimate in metrics.items():
                self.add_estimate(self.nv(resource, metric) == estimate)

    def check(self):
        return self._solver.check()

    def sexpr(self):
        return self._solver.sexpr()
