# IaC Analysis

## 1. Prerequisites

### 1.1. Install `poetry`
The project is built with [poetry](https://python-poetry.org/). Please install it first.

After installing `poetry`, I recommend using the following command to configure `poetry` to put the python virtual environments in the directory of each project:

```shell
poetry config virtualenvs.in-project true
```

This helps VSCode to identify and start using the virtual environments.

### 1.2. Install project dependencies
Inside the project directory, you need to install the project's dependencies. You can do this by running the following command:

```shell
poetry install
```

This will create a virtual environment and install all the project's dependencies into it.


## 2. Usage

The main command, `iac-analysis`:
```shell
poetry run iac-analysis --help
```

To output a graph of the infrastruture, use `poetry run iac-analysis graph [CFN_FILE]`.

To output resource usage estimates template, use `poetry run iac-analysis estimates-template [CFN_FILE]`.

To show more information about the infrastructure and generated constraints, use `poetry run iac-analysis constrain [CFN_FILE]`.

This `check` sub-command checks whether the usage estimates satisfy the constraints of the infrastructure.
```shell
poetry run iac-analysis check [CFN_FILE] [USAGE_ESTIMATES]
```

The `constrain` and `check` subcommands support `-c` flag to supply custom constraint generator in the form of a Python module, which should export a function named `compute_constraints`. You may look at `./example_custom_constraints.py` as an example.