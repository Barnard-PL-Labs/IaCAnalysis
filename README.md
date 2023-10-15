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

Currently, there is only one sub-command, `check`:
```shell
poetry run iac-analysis check --help
```

This `check` sub-command checks whether the Infracost usage estimates satisfy the constraints of the Terraform infrastructures. For example:
```shell
poetry run iac-analysis examples/sqs-lambda-trigger/tfplan.json examples/sqs-lambda-trigger/infracost-usage.yml
```

## 3. Supported cloud platforms and services

AWS:
- Lambda
- SQS
- Lambda Event Source Mapping

## 4. Viewing Terraform configuration

How to view parsed Terraform configuration:
1. `terraform plan -out tfplan.binary`
2. `terraform show -json tfplan.binary`

The configuration specified by the (.tf) files will be in the `configuration` attribute in the JSON.
For more information, see Terraform docomentation on [configuration representation](https://developer.hashicorp.com/terraform/internals/json-format#configuration-representation).

## 5. Using Infracost

Generate a new usage file (named `infracost-usage.yml`) and show a breakdown:
```shell
infracost breakdown --sync-usage-file --usage-file infracost-usage.yml --path .
```