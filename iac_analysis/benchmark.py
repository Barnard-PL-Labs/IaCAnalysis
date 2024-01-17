from typing import Optional
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


app = typer.Typer()

benchmarks_path = "benchmarks"


def version_callback(value: bool) -> None:
    if value:
        print(f"{__app_name__} benchmark v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show the version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """
    Benchmark commands for IaC analysis
    """
    logging_level = logging.ERROR
    logging.basicConfig(level=logging_level)


@app.command()
def run(
    benchmark_name: Annotated[str, typer.Argument(help="Benchmark name")],
    cfn_template: Annotated[str, typer.Argument(help="CloudFormation template")],
    custom_smt2: Annotated[
        Optional[str],
        typer.Option("--custom-smt2", help="Additional custom SMT2 constraint"),
    ] = None,
) -> None:
    """
    Run benchmark on a CFN template
    """
    infra = Infra.from_cfn(cfn_template)
    s = solver.Solver()
    infra.compute_constraints(s)
    if custom_smt2:
        parsed_custom_smt2 = solver.parse_smt2_file(custom_smt2)
        s.add(parsed_custom_smt2)

    number_of_resources = len(infra.resources)
    average_degree = infra.average_degree()
    number_of_constraints = len(s.constraints)
    number_of_custom_constraints = 0 if custom_smt2 is None else len(parsed_custom_smt2)

    cmd = ["iac-analysis", "benchmark-constrain", cfn_template]
    if custom_smt2:
        cmd.append(custom_smt2)
    generate_constraints_ms = time_shell_command_in_ms(cmd)

    print(
        f"{benchmark_name},{number_of_resources},{average_degree},{number_of_custom_constraints},{number_of_constraints},{generate_constraints_ms}"
    )


@app.command()
def single(
    benchmark_name: Annotated[str, typer.Argument(help="Benchmark name")],
) -> None:
    """
    Single benchmark
    """
    cfn_path = os.path.join(benchmarks_path, benchmark_name, "cfn.yaml")
    custom_smt2_path = os.path.join(benchmarks_path, benchmark_name, "custom.smt2")

    if os.path.exists(custom_smt2_path):
        run(
            benchmark_name=benchmark_name,
            cfn_template=cfn_path,
            custom_smt2=custom_smt2_path,
        )
    else:
        run(benchmark_name=benchmark_name, cfn_template=cfn_path)


@app.command()
def all():
    """
    Full benchmark set
    """
    subdirectories = sorted(
        [
            d
            for d in os.listdir(benchmarks_path)
            if os.path.isdir(os.path.join(benchmarks_path, d))
        ]
    )
    for benchmark_name in subdirectories:
        single(benchmark_name=benchmark_name)


# HELPERS
def time_shell_command_in_ms(cmd):
    # Record the start time
    start_time = time.time()

    # Run the shell command using subprocess
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    # Record the end time
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    return elapsed_time * 1000
