# IaC Analysis

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