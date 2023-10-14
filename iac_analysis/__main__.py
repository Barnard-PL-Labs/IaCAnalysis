"""IaC Analysis entry point script"""
# iac_analysis/__main__.py

from iac_analysis import cli, __app_name__

def main():
    cli.app(prog_name = __app_name__)

