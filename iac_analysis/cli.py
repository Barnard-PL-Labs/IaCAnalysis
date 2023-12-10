"""CLI for IaC Analysis"""
# iac_analysis/cli.py

from typing import Optional
import typer
from typing_extensions import Annotated
import logging
import z3
import yaml

from iac_analysis import __app_name__, __version__
from iac_analysis.infra import Infra
from iac_analysis import solver
from iac_analysis.estimates import load_estimates, generate_estimates_template


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
    cfn_template: Annotated[str, typer.Argument(help="CloudFormation template")],
    estimates_file: Annotated[str, typer.Argument(help="Estimates file")],
) -> None:
    """
    Check whether the usage estimates satisfy the constraints of the infrastructure.
    """
    usage = load_estimates(estimates_file)
    infra = Infra.from_cfn(cfn_template)
    s = solver.Solver()
    infra.compute_constraints(s)
    s.add_estimates(infra.resources, usage)
    print("z3 solver constraints: \n%s", s.sexpr())

    result = s.check()
    if result == z3.sat:
        print("✅ The usage estimates satisfy the constraints of the infrastructure")
    elif result == z3.unsat:
        print(
            "❌ The usage estimates did not satisfy the constraints of the infrastructure"
        )
    else:
        print("⚠️ The solver failed to solve the constraints")


@app.command()
def estimates_template(
    cfn_template: Annotated[str, typer.Argument(help="CloudFormation template")],
) -> None:
    """
    Generate a template estimates file file for the given CloudFormation template.
    """
    infra = Infra.from_cfn(cfn_template)
    usage_template = generate_estimates_template(infra)
    print(yaml.safe_dump(usage_template))


@app.command()
def constrain(
    cfn_template: Annotated[str, typer.Argument(help="CloudFormation template")],
) -> None:
    """
    Produce constraints for the infrastructure specified in the given CloudFormation template.
    """
    infra = Infra.from_cfn(cfn_template)
    print()
    print("--- RESOURCES ---")
    print(infra.resources)
    print()
    print("--- EDGES ---")
    infra.print_edges()
    s = solver.Solver()
    infra.compute_constraints(s)
    print()
    print("--- CONSTRAINTS ---")
    print(f"count: {len(s.constraints)}")
    for i, c in enumerate(s.constraints):
        print(f"{i+1}: ", c)


@app.command()
def graph(
    cfn_template: Annotated[str, typer.Argument(help="CloudFormation template")],
    file_name: Annotated[
        str, typer.Argument(help="File name for graph PNG")
    ] = "graph.png",
) -> None:
    """
    Generate PNG image for the infrastructure graph.
    """
    infra = Infra.from_cfn(cfn_template)
    infra.draw(file_name)
