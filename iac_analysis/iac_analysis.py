import argparse
import json
import logging
import yaml
import z3

### Constants

TF_AWS_LAMBDA_FUNCTION = "aws_lambda_function"
TF_AWS_SQS_QUEUE = "aws_sqs_queue"
TF_AWS_LAMBDA_EVENT_SOURCE_MAPPING = "aws_lambda_event_source_mapping"

### General setup
logger = logging.getLogger(__name__)


### Helper functions
def find_first(l, predicate):
    return next((item for item in l if predicate(item)), None)


def infracost_metric_usage_with_callback(
    infracost_usage, address, resource_type, metric, callback
):
    try:
        callback(infracost_usage["resource_usage"][address][metric])
    except KeyError:
        try:
            callback(
                infracost_usage["resource_type_default_usage"][resource_type][metric]
            )
        except KeyError:
            pass


### Infracost
def read_infracost_usage_yaml(fpath):
    with open(fpath, "r") as f:
        return yaml.safe_load(f)


### Terraform
def read_tf_plan_json(fpath):
    with open(fpath, "r") as f:
        return json.load(f)


def tf_plan_managed_resources(tf_plan):
    resources = tf_plan["configuration"]["root_module"]["resources"]
    # filter by 'mode':
    #   - data block: mode == 'data'
    #   - resource block: mode == 'managed'
    managed_resources = {r["address"]: r for r in resources if r["mode"] == "managed"}
    return managed_resources


### Main driver
def run_iac_analysis(tf_plan, infracost_usage):
    logger.debug(tf_plan)
    logger.debug(infracost_usage)

    # map of managed resources, indexed from address to resource
    managed_resources = tf_plan_managed_resources(tf_plan)
    logger.debug(managed_resources)

    # generate a set of z3 variables for each resource
    # different for each resource type
    resources_vars_map = {}
    for address, resource in managed_resources.items():
        resource_type = resource["type"]
        vars = {}
        if resource_type == TF_AWS_LAMBDA_FUNCTION:
            vars["monthly_requests"] = z3.Int(address + ".monthly_requests")
            vars["requests_duration_ms"] = z3.Int(address + ".requests_duration_ms")
        elif resource_type == TF_AWS_SQS_QUEUE:
            vars["monthly_requests"] = z3.Int(address + ".monthly_requests")
            vars["request_size_kb"] = z3.Int(address + ".requests_duration_ms")
        resources_vars_map[address] = vars

    # generate constraints for each resource
    solver = z3.Solver()
    for address, resource in managed_resources.items():
        resource_type = resource["type"]
        if resource_type == TF_AWS_LAMBDA_EVENT_SOURCE_MAPPING:
            # get address for event_source_arn
            event_source_arn_references = resource["expressions"]["event_source_arn"][
                "references"
            ]
            event_source_address = find_first(
                event_source_arn_references, lambda x: x in managed_resources
            )
            if event_source_address is None:
                logger.error("Not a valid event source: ", event_source_address)

            # get address for function_name
            function_name_references = resource["expressions"]["function_name"][
                "references"
            ]
            function_address = find_first(
                function_name_references, lambda x: x in managed_resources
            )
            if function_address is None:
                logger.error("Not a valid function name: ", function_address)

            # constraints for aws_lambda_event_source_mapping:
            #   1. if event source is SQS, then sqs.monthly_requests >= lambda.monthly_requests
            if managed_resources[event_source_address]["type"] == TF_AWS_SQS_QUEUE:
                solver.add(
                    resources_vars_map[event_source_address]["monthly_requests"]
                    >= resources_vars_map[function_address]["monthly_requests"]
                )

    # add Infracost usage estimates as constraints
    # first, resource type default usage estimates
    for address, resource in managed_resources.items():
        vars = resources_vars_map[address]
        resource_type = resource["type"]
        if resource_type == TF_AWS_LAMBDA_FUNCTION:
            infracost_metric_usage_with_callback(
                infracost_usage,
                address,
                resource_type,
                "monthly_requests",
                lambda x: solver.add(vars["monthly_requests"] == x),
            )
            infracost_metric_usage_with_callback(
                infracost_usage,
                address,
                resource_type,
                "requests_duration_ms",
                lambda x: solver.add(vars["monthly_requests"] == x),
            )
        elif resource_type == TF_AWS_SQS_QUEUE:
            infracost_metric_usage_with_callback(
                infracost_usage,
                address,
                resource_type,
                "monthly_requests",
                lambda x: solver.add(vars["monthly_requests"] == x),
            )
            infracost_metric_usage_with_callback(
                infracost_usage,
                address,
                resource_type,
                "request_size_kb",
                lambda x: solver.add(vars["monthly_requests"] == x),
            )

    # run solver
    solver_result = solver.check()

    return solver_result


def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="IaC analysis")

    # Add command-line arguments
    parser.add_argument(
        "-f", "--file", help="Path to a Terraform plan JSON file", required=True
    )
    parser.add_argument(
        "-u", "--usage", help="Path to an Infracost usage YAML file", required=True
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose mode"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values of the arguments
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    if args.file and args.usage:
        tf_plan = read_tf_plan_json(args.file)
        infracost_usage = read_infracost_usage_yaml(args.usage)
        solver_result = run_iac_analysis(tf_plan, infracost_usage)

        if solver_result == z3.sat:
            logger.info(
                "The usage estimates satisfy the constraints of the infrastructure"
            )
        elif solver_result == z3.unsat:
            logger.warning(
                "The usage estimates did not satisfy the constraints of the infrastructure"
            )
        else:
            logger.error("The solver failed to solve the constraints")


if __name__ == "__main__":
    main()
