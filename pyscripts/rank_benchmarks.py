from typing import Optional
import sys
import typer
from typing_extensions import Annotated
import logging
from pathlib import Path
import os
import subprocess
import time

from iac_analysis import __app_name__, __version__
from iac_analysis.infra import Infra
from iac_analysis import solver
from iac_analysis.estimates import load_estimates, generate_estimates_template
from iac_analysis.custom_generator import load_custom_generator
import iac_analysis.cfn as cfn
from iac_analysis.resource import (
    Resource,
    supported_resource_types,
    ignore_resource_types,
    public_usage_metrics,
)


app = typer.Typer()


@app.callback()
def main() -> None:
    """
    Benchmark commands for IaC analysis
    """
    logging_level = logging.ERROR
    logging.basicConfig(level=logging_level)


@app.command()
def rank_by_supported(
    benchmarks_dir: Annotated[str, typer.Argument(help="Path to benchmarks directory")],
) -> None:
    """
    Rank benchmarks by number of supported resources
    """

    benchmarks = os.listdir(benchmarks_dir)

    records = []

    for benchmark in benchmarks:
        benchmark_path = os.path.join(benchmarks_dir, benchmark)
        n = count_supported_resources(benchmark_path)
        if n is None:
            continue
        records.append((n, benchmark))

    ranked_records = sorted(records, reverse=True)

    for n, benchmark in ranked_records:
        print(f"{benchmark}, {n}")


@app.command()
def rank_by_constraints(
    benchmarks_dir: Annotated[str, typer.Argument(help="Path to benchmarks directory")],
) -> None:
    """
    Rank benchmarks by number of supported resources
    """

    benchmarks = os.listdir(benchmarks_dir)

    records = []

    for benchmark in benchmarks:
        benchmark_path = os.path.join(benchmarks_dir, benchmark)
        n = count_supported_resources(benchmark_path)
        if n is None:
            continue
        try:
            infra = Infra.from_cfn(benchmark_path)
            s = solver.Solver()
            infra.compute_constraints(s)
            records.append((len(s.constraints), benchmark))
        except:
            print(benchmark_path, file=sys.stderr)

    ranked_records = sorted(records, reverse=True)

    for n, benchmark in ranked_records:
        print(f"{benchmark}, {n}")


def count_supported_resources(fpath):
    c = cfn.load_template(fpath)
    if c is None:
        return None
    if "Resources" not in c:
        return None

    n = 0
    for name, body in c["Resources"].items():
        resource_type = body["Type"]
        if resource_type in supported_resource_types:
            n += 1
    return n
