"""CLI for IaC Analysis"""
# iac_analysis/cli.py

from typing import Optional
import typer
from typing_extensions import Annotated
import logging
import z3

from iac_analysis import __app_name__, __version__
from iac_analysis.infrastructure import Infrastructure
from iac_analysis import infracost


app = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        print(f"{__app_name__} v{__version__}")
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
    debug: Annotated[
        Optional[bool],
        typer.Option(
            "--debug",
            "-d",
            help="Enable debug mode for more detailed tracing.",
        ),
    ] = None,
) -> None:
    """
    IaC analysis tool.
    """
    logging_level = logging.INFO
    if debug:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level)


@app.command()
def check(
    tf_plan: Annotated[str, typer.Argument(help="Terraform plan file in JSON")],
    ic_usage: Annotated[str, typer.Argument(help="Infracost usage file in YAML")],
) -> None:
    """
    Check whether the Infracost usage estimates satisfy the constraints of the Terraform infrastructures.
    """
    infra = Infrastructure.from_terraform_plan_path(tf_plan)
    solver = z3.Solver()

    # infrastructure constraints
    for constraint in infra.constraints:
        solver.add(constraint)

    # infracost usage constraints
    usage = infracost.read_usage_yaml(ic_usage)
    usage_constraints = infra.generate_infracost_usage_constraints(usage)
    for constraint in usage_constraints:
        solver.add(constraint)

    result = solver.check()
    print("z3 solver constraints: \n%s", solver.sexpr())

    if result == z3.sat:
        print("✅ The usage estimates satisfy the constraints of the infrastructure")
    elif result == z3.unsat:
        print(
            "❌ The usage estimates did not satisfy the constraints of the infrastructure"
        )
    else:
        print("⚠️ The solver failed to solve the constraints")
