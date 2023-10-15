"""CLI for IaC Analysis"""
# iac_analysis/cli.py

from typing import Optional
import typer
from typing_extensions import Annotated
import logging

from iac_analysis import __app_name__, __version__
import iac_analysis.analysis as analysis


app = typer.Typer()


def version_callback(value: bool):
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
):
    """
    Check whether the Infracost usage estimates satisfy the constraints of the Terraform infrastructures.
    """
    result = analysis.run_iac_analysis_with_paths(tf_plan, ic_usage)

    if result == analysis.SAT:
        print("✅ The usage estimates satisfy the constraints of the infrastructure")
    elif result == analysis.UNSAT:
        print(
            "❌ The usage estimates did not satisfy the constraints of the infrastructure"
        )
    else:
        print("⚠️ The solver failed to solve the constraints")
