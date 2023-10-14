"""CLI for IaC Analysis"""
# iac_analysis/cli.py

from typing import Optional
import typer
from typing_extensions import Annotated

from iac_analysis import __app_name__, __version__

app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(f"{__app_name__} v{__version__}")
        raise typer.Exit()


def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    return
