import json
import sys
from typing import Dict, Any, List
import z3
from enum import Enum, auto

from iac_analysis import infracost

MONTHLY_REQUESTS = "monthly_requests"


class Op(Enum):
    ADD = auto()


class Update:
    def __init__(self, metric, op, value):
        self.metric = metric
        self.op = op
        self.value = value


class Connection:
    def __init__(self, source, destination, updates=[]):
        self.source = source
        self.destination = destination
        self.updates = updates


class Resource:
    AWS_LAMBDA = "aws_lambda_function"
    AWS_SQS = "aws_sqs_queue"
    AWS_LAMBDA_EVENT_SOURCE_MAPPING = "aws_lambda_event_source_mapping"
    supported_types = [AWS_LAMBDA, AWS_SQS, AWS_LAMBDA_EVENT_SOURCE_MAPPING]

    def __init__(self, address: str, type: str, name: str, params: str):
        self.address = address
        self.type = type
        self.name = name
        self.params = params
        self.in_connections = []
        self.out_connections = []
        self._solver_variables = {}

    def solver_variable(self, key: str):
        if not key in self._solver_variables:
            self._solver_variables[key] = z3.Int(f"{self.address}.{key}")
        return self._solver_variables[key]

    def add_in_connection(self, connection):
        self.in_connections.append(connection)

    def add_out_connection(self, connection):
        self.out_connections.append(connection)

    @classmethod
    def from_terraform_plan(cls, resource: Dict[str, Any]):
        return cls(
            resource["address"],
            resource["type"],
            resource["name"],
            resource["expressions"],
        )


class Infrastructure:
    def __init__(self, resources: List[Resource]):
        self.resources = {r.address: r for r in resources}
        self.compute_connections()
        self.compute_constraints()

    def compute_connections(self):
        self.connections = []
        for resource in self.resources.values():
            if resource.type == Resource.AWS_LAMBDA_EVENT_SOURCE_MAPPING:
                # get resource referenced by event_source_arn
                event_source = self.find_reference(
                    resource.params["event_source_arn"]["references"]
                )
                if event_source is None:
                    sys.exit(f"{resource.address} does not have a valid event_source.")

                # get resource referenced by function_name
                lambda_function = self.find_reference(
                    resource.params["function_name"]["references"]
                )
                if lambda_function is None:
                    sys.exit(f"{resource.address} does not have a valid function_name.")

                self.add_connection(
                    resource,
                    lambda_function,
                    updates=[
                        Update(
                            MONTHLY_REQUESTS,
                            Op.ADD,
                            resource.solver_variable(MONTHLY_REQUESTS),
                        )
                    ],
                )
                self.add_connection(
                    event_source,
                    resource,
                    updates=[
                        Update(
                            MONTHLY_REQUESTS,
                            Op.ADD,
                            event_source.solver_variable(MONTHLY_REQUESTS),
                        )
                    ],
                )

    def find_reference(self, references):
        find_first = lambda l, pred: next((item for item in l if pred(item)), None)
        address = find_first(references, lambda x: x in self.resources)
        return self.resources[address] if address else None

    def add_connection(self, source, destination, updates=[]):
        connection = Connection(source, destination, updates=updates)
        destination.add_in_connection(connection)
        source.add_out_connection(connection)
        self.connections.append(connection)

    def compute_constraints(self):
        self.constraints = []
        for resource in self.resources.values():
            # check monthly_requests ADD operation
            adds = []
            for connection in resource.in_connections:
                for update in connection.updates:
                    if update.metric == MONTHLY_REQUESTS and update.op == Op.ADD:
                        adds.append(update.value)
            if len(adds) > 0:
                self.constraints.append(
                    resource.solver_variable(MONTHLY_REQUESTS) >= sum(adds[1:], adds[0])
                )

    def generate_infracost_usage_constraints(self, usage):
        constraints = []

        for address, resource in self.resources.items():
            if resource.type == Resource.AWS_LAMBDA:
                infracost.metric_usage_with_callback(
                    usage,
                    address,
                    resource.type,
                    "monthly_requests",
                    lambda x: constraints.append(
                        resource.solver_variable("monthly_requests") == x
                    ),
                )
                infracost.metric_usage_with_callback(
                    usage,
                    address,
                    resource.type,
                    "requests_duration_ms",
                    lambda x: constraints.append(
                        resource.solver_variable("requests_duration_ms") == x
                    ),
                )
            elif resource.type == Resource.AWS_SQS:
                infracost.metric_usage_with_callback(
                    usage,
                    address,
                    resource.type,
                    "monthly_requests",
                    lambda x: constraints.append(
                        resource.solver_variable("monthly_requests") == x
                    ),
                )
                infracost.metric_usage_with_callback(
                    usage,
                    address,
                    resource.type,
                    "request_size_kb",
                    lambda x: constraints.append(
                        resource.solver_variable("request_size_kb") == x
                    ),
                )
        return constraints

    @classmethod
    def from_terraform_plan(cls, tfplan: Dict[str, Any]):
        resources = tfplan["configuration"]["root_module"]["resources"]
        resources = [Resource.from_terraform_plan(r) for r in resources]
        return cls(resources)

    @classmethod
    def from_terraform_plan_path(cls, fpath: str):
        with open(fpath, "r") as f:
            tfplan = json.load(f)
        return cls.from_terraform_plan(tfplan)
