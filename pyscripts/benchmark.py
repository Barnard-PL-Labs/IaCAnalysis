from typing import Optional
import csv
import typer
from typing_extensions import Annotated
import logging
from pathlib import Path
import os
import subprocess
import time
import sys

from iac_analysis import __app_name__, __version__
from iac_analysis.infra import Infra
from iac_analysis import solver
from iac_analysis.estimates import load_estimates, generate_estimates_template
from iac_analysis.custom_generator import load_custom_generator


app = typer.Typer()


@app.callback()
def main() -> None:
    """
    Benchmark commands for IaC analysis
    """
    logging_level = logging.ERROR
    logging.basicConfig(level=logging_level)


@app.command()
def one(
    benchmark_path: Annotated[str, typer.Argument(help="Benchmark path")],
) -> None:
    """
    Single benchmark
    """
    record = run(benchmark_path)
    writer = benchmarks_writer()
    writer.writerow(record)


@app.command()
def all(
    benchmarks_path: Annotated[str, typer.Argument(help="Benchmarks directory path")],
):
    """
    Full benchmark set
    """
    benchmarks = sorted(
        [os.path.join(benchmarks_path, d) for d in os.listdir(benchmarks_path)]
    )
    # records = [run(benchmark) for benchmark in benchmarks]
    records = []
    for benchmark in benchmarks:
        try:
            records.append(run(benchmark))
        except TypeError:
            print(benchmark, file=sys.stderr)
        except KeyError:
            print("KEYERROR", benchmark, file=sys.stderr)

    writer = benchmarks_writer()
    writer.writerows(records)


def benchmarks_writer():
    fieldnames = [
        "benchmark_name",
        "number_of_resources",
        "number_of_supported_resources",
        "number_of_ignored_resources",
        "number_of_unsupported_resources",
        "number_of_lambdas",
        "number_of_ec2",
        "average_graph_degree",
        "number_of_constraints",
        "number_of_basic_constraints",
        "number_of_incoming_constraints",
        "number_of_intrinsic_constraints",
        "number_of_outgoing_constraints",
        "time_to_generate_constraints_in_ms",
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    return writer


def run(benchmark_path):
    infra = Infra.from_cfn(benchmark_path)
    s = solver.Solver()
    infra.compute_constraints(s)

    cmd = ["iac-analysis", "benchmark-constrain", benchmark_path]
    result, time_to_generate_constraints_in_ms = time_shell_command_in_ms(cmd)
    if result.stdout.decode() != "Done\n":
        os.exit(f"Did not successfully run benchmark {benchmark_path}")

    return {
        "benchmark_name": os.path.basename(benchmark_path),
        "number_of_resources": infra.number_of_resources,
        "number_of_supported_resources": infra.number_of_supported_resources,
        "number_of_ignored_resources": infra.number_of_ignored_resources,
        "number_of_unsupported_resources": infra.number_of_unsupported_resources,
        "number_of_lambdas": infra.number_of_lambdas,
        "number_of_ec2": infra.number_of_ec2,
        "average_graph_degree": infra.average_degree(),
        "number_of_constraints": len(s.constraints),
        "number_of_basic_constraints": s.number_of_basic,
        "number_of_intrinsic_constraints": s.number_of_intrinsic,
        "number_of_incoming_constraints": s.number_of_incoming,
        "number_of_outgoing_constraints": s.number_of_outgoing,
        "time_to_generate_constraints_in_ms": time_to_generate_constraints_in_ms,
    }


# HELPERS
def time_shell_command_in_ms(cmd):
    # Record the start time
    start_time = time.time()

    # Run the shell command using subprocess
    # process = subprocess.Popen(
    #     cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    # )
    # stdout, stderr = process.communicate()
    # print(stdout)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Record the end time
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    return result, elapsed_time * 1000
