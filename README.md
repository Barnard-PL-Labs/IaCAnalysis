# IaC Analysis

## Usage

```
$ python iac_analysis/iac_analysis.py --help
usage: iac_analysis.py [-h] -f FILE -u USAGE [-v]

IaC analysis

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to a Terraform plan JSON file
  -u USAGE, --usage USAGE
                        Path to an Infracost usage YAML file
  -v, --verbose         Enable verbose mode
  ```

Example:
```shell
python iac_analysis/iac_analysis.py -v -f examples/sqs-lambda-trigger/tfplan.json -u examples/sqs-lambda-trigger/infracost-usage.yml
```

## Supported cloud platforms and services

AWS:
- Lambda
- SQS
- Lambda Event Source Mapping

## Viewing Terraform configuration

How to view parsed Terraform configuration:
1. `terraform plan -out tfplan.binary`
2. `terraform show -json tfplan.binary`

The configuration specified by the (.tf) files will be in the `configuration` attribute in the JSON.
For more information, see Terraform docomentation on [configuration representation](https://developer.hashicorp.com/terraform/internals/json-format#configuration-representation).

## Using Infracost

Generate a new usage file (named `infracost-usage.yml`) and show a breakdown:
```shell
infracost breakdown --sync-usage-file --usage-file infracost-usage.yml --path .
```