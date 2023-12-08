import z3


class Solver:
    def __init__(self):
        self.pool = {}
        self.constraints = []

    def nv(self, resource, metric):
        varname = f"{resource}.{metric}"
        if not varname in self.pool:
            self.pool[varname] = z3.Int(varname)
        return self.pool[varname]

    def ev(self, source, destination, metric):
        varname = f"{source}_{destination}.{metric}"
        if not varname in self.pool:
            self.pool[varname] = z3.Int(varname)
        return self.pool[varname]

    def add(self, constraint):
        self.constraints.append(constraint)

    def check(self):
        solver = z3.Solver()
        solver.add(*self.constraints)
        return solver.check()
