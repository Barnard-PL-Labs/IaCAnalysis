from typing import Optional
import typer
from typing_extensions import Annotated
import logging
from pathlib import Path
import subprocess
import time

from iac_analysis import __app_name__, __version__
from iac_analysis.infra import Infra
from iac_analysis import solver
from iac_analysis.estimates import load_estimates, generate_estimates_template
from iac_analysis.custom_generator import load_custom_generator


app = typer.Typer()

benchmarks = [
    ("examples/sns-lambda-alias.yaml", "custom.smt2"),
]


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
def single(
    cfn_template: Annotated[str, typer.Argument(help="CloudFormation template")],
    custom_smt2: Annotated[
        Optional[str],
        typer.Option("--custom-smt2", help="Additional custom SMT2 constraint"),
    ] = None,
) -> None:
    """
    Benchmark a single CFN template
    """
    infra = Infra.from_cfn(cfn_template)
    s = solver.Solver()
    infra.compute_constraints(s)
    if custom_smt2:
        parsed_custom_smt2 = solver.parse_smt2_file(custom_smt2)
        s.add(parsed_custom_smt2)

    benchmark_name = Path(cfn_template).stem
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
def all():
    """
    Full benchmark
    """
    for cfn_template, custom_smt2 in benchmarks:
        single(cfn_template=cfn_template, custom_smt2=custom_smt2)


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
