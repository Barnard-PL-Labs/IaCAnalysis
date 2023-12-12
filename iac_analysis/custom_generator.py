import importlib
import sys


def load_custom_generator(custom_generator_module):
    m = importlib.import_module(custom_generator_module)
    if hasattr(m, "compute_constraints"):
        return m.compute_constraints
    else:
        sys.exit(
            "The user-provided custom constraint generator module does not provide a 'compute_constraints' function"
        )
