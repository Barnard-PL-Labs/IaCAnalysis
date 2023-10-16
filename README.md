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

To show debugging information (e.g. z3 solver constraints), use the `--debug` flag:
```shell
poetry run iac-analysis --debug ......
```

This `check` sub-command checks whether the Infracost usage estimates satisfy the constraints of the Terraform infrastructures. For example:
```shell
poetry run iac-analysis check examples/sqs-lambda-trigger/tfplan.json examples/sqs-lambda-trigger/infracost-usage.yml
```

There is a script that runs an example for you:
```shell
./run_example examples/{sqs-lambda-trigger}
```

## 3. Supported cloud platforms and services

AWS:
- Lambda
- SQS
- Lambda Event Source Mapping

## 4. Viewing Terraform configuration

First, go into the directory that contains the example that you want to use.
```shell
cd examples/{EXAMPLE}
```

Initialize the terraform project:
```shell
terraform init
```

Generate a Terraform Plan JSON file:
```shell
terraform plan -out tfplan.binary
terraform show -json tfplan.binary > tfplan.json
```

The configuration specified by the (.tf) files will be in the `configuration` attribute in the JSON.
For more information, see Terraform docomentation on [configuration representation](https://developer.hashicorp.com/terraform/internals/json-format#configuration-representation).

## 5. Using Infracost

First, go into the directory that contains the example that you want to use.
```shell
cd examples/{EXAMPLE}
```
Generate a new usage file (named `infracost-usage.yml`) and show a breakdown:
```shell
infracost breakdown --sync-usage-file --usage-file infracost-usage.yml --path .
```