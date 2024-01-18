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
def stats(
    benchmarks_dir: Annotated[str, typer.Argument(help="Path to benchmarks directory")],
) -> None:
    """
    Some statistics about the benchmarks
    """
    benchmarks_dir = os.path.abspath(benchmarks_dir)

    os.chdir(benchmarks_dir)

    benchmarks = sorted(
        [
            d
            for d in os.listdir(benchmarks_dir)
            if os.path.isdir(os.path.join(benchmarks_dir, d))
        ]
    )

    total_number = 0
    total_number_of_cdk = 0
    total_number_of_ts_cdk_with_multiple_cdk_json = 0
    total_number_of_ts_cdk = 0

    for benchmark in benchmarks:
        number_of_cdk_json = 0

        dpaths = [
            dpath for dpath, _, files in os.walk(benchmark) if "cdk.json" in files
        ]
        for dpath in dpaths:
            if os.path.exists(os.path.join(dpath, "package.json")):
                number_of_cdk_json += 1

        total_number += 1
        if len(dpaths) > 0:
            total_number_of_cdk += 1
        if number_of_cdk_json > 1:
            total_number_of_ts_cdk_with_multiple_cdk_json += 1
        if number_of_cdk_json > 0:
            total_number_of_ts_cdk += 1

    print("Total number: ", total_number)
    print("Total number of CDK: ", total_number_of_cdk)
    print("Total number of TS CDK: ", total_number_of_ts_cdk)
    print(
        "Total number of TS CDK with multiple cdk.json: ",
        total_number_of_ts_cdk_with_multiple_cdk_json,
    )


@app.command()
def gen_cfn(
    benchmarks_dir: Annotated[str, typer.Argument(help="Path to benchmarks directory")],
    output_dir: Annotated[str, typer.Argument(help="Output directory")],
) -> None:
    """
    Turn CDK benchmarks into CloudFormation templates
    """
    benchmarks_dir = os.path.abspath(benchmarks_dir)
    output_dir = os.path.abspath(output_dir)

    os.chdir(benchmarks_dir)

    benchmarks = sorted(
        [
            d
            for d in os.listdir(benchmarks_dir)
            if os.path.isdir(os.path.join(benchmarks_dir, d))
        ]
    )

    for benchmark in benchmarks:
        dpaths = [
            dpath for dpath, _, files in os.walk(benchmark) if "cdk.json" in files
        ]
        if len(dpaths) == 1:
            dpath = dpaths[0]
            if os.path.exists(os.path.join(dpath, "package.json")):
                os.chdir(dpath)
                npm_success = run_cmd_stdout(["npm", "install"])
                cfn, cdk_success = run_cmd_stdout(["cdk", "synth"])
                run_cmd(["rm", "-rf", "node_modules"])
                os.chdir(benchmarks_dir)

                if npm_success and cdk_success:
                    with open(
                        os.path.join(output_dir, f"{benchmark}.yaml"), "wb"
                    ) as binary_file:
                        binary_file.write(cfn)


def run_cmd_stdout(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout, result.returncode == 0


def run_cmd(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.returncode == 0
