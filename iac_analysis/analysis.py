from enum import Enum
import z3
import logging
import iac_analysis.terraform as tf
from iac_analysis.helpers import find_first
import iac_analysis.infracost as ic

logger = logging.getLogger(__name__)

(SAT, UNSAT, UNKNOWN) = range(3)


class Result(Enum):
    SAT = 0
    UNSAT = 1
    UNKNOWN = 2


def run_iac_analysis_with_paths(tf_plan_path: str, ic_usage_path: str) -> Result:
    tf_plan = tf.read_plan_json(tf_plan_path)
    ic_usage = ic.read_usage_yaml(ic_usage_path)
    return run_iac_analysis(tf_plan, ic_usage)


def run_iac_analysis(tf_plan, infracost_usage):
    # map of managed resources, indexed from address to resource
    managed_resources = tf.plan_managed_resources(tf_plan)

    # generate a set of z3 variables for each resource
    # different for each resource type
    resources_vars_map = {}
    for address, resource in managed_resources.items():
        resource_type = resource["type"]
        vars = {}
        if resource_type == tf.AWS_LAMBDA_FUNCTION:
            vars["monthly_requests"] = z3.Int(address + ".monthly_requests")
            vars["requests_duration_ms"] = z3.Int(address + ".requests_duration_ms")
        elif resource_type == tf.AWS_SQS_QUEUE:
            vars["monthly_requests"] = z3.Int(address + ".monthly_requests")
            vars["request_size_kb"] = z3.Int(address + ".request_size_kb")
        resources_vars_map[address] = vars

    # generate constraints for each resource
    solver = z3.Solver()
    for address, resource in managed_resources.items():
        resource_type = resource["type"]
        if resource_type == tf.AWS_LAMBDA_EVENT_SOURCE_MAPPING:
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
            if managed_resources[event_source_address]["type"] == tf.AWS_SQS_QUEUE:
                solver.add(
                    resources_vars_map[event_source_address]["monthly_requests"]
                    >= resources_vars_map[function_address]["monthly_requests"]
                )

    # add Infracost usage estimates as constraints
    # first, resource type default usage estimates
    for address, resource in managed_resources.items():
        vars = resources_vars_map[address]
        resource_type = resource["type"]
        if resource_type == tf.AWS_LAMBDA_FUNCTION:
            ic.metric_usage_with_callback(
                infracost_usage,
                address,
                resource_type,
                "monthly_requests",
                lambda x: solver.add(vars["monthly_requests"] == x),
            )
            ic.metric_usage_with_callback(
                infracost_usage,
                address,
                resource_type,
                "requests_duration_ms",
                lambda x: solver.add(vars["monthly_requests"] == x),
            )
        elif resource_type == tf.AWS_SQS_QUEUE:
            ic.metric_usage_with_callback(
                infracost_usage,
                address,
                resource_type,
                "monthly_requests",
                lambda x: solver.add(vars["monthly_requests"] == x),
            )
            ic.metric_usage_with_callback(
                infracost_usage,
                address,
                resource_type,
                "request_size_kb",
                lambda x: solver.add(vars["monthly_requests"] == x),
            )

    # run solver
    solver_result = solver.check()
    logger.debug("z3 solver constraints: \n%s", solver.sexpr())

    if solver_result == z3.sat:
        return SAT
    elif solver_result == z3.unsat:
        return UNSAT
    else:
        return UNKNOWN
