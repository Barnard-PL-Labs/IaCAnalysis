"""Top-level package for IaC Analaysis tool"""
# iac_analysis/__init__.py

__app_name__ = "iac_analysis"
__version__ = "0.1.0"

(
    SUCCESS,
    SOLVER_ERROR,
) = range(2)

ERRORS = {SOLVER_ERROR: "solver error"}
