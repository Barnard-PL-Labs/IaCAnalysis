import json
from typing import Dict, Any

AWS_LAMBDA_FUNCTION = "aws_lambda_function"
AWS_SQS_QUEUE = "aws_sqs_queue"
AWS_LAMBDA_EVENT_SOURCE_MAPPING = "aws_lambda_event_source_mapping"


def read_plan_json(fpath: str) -> Dict[str, Any]:
    with open(fpath, "r") as f:
        return json.load(f)


def plan_managed_resources(tf_plan: Dict[str, Any]) -> Dict[str, Any]:
    resources = tf_plan["configuration"]["root_module"]["resources"]
    # filter by 'mode':
    #   - data block: mode == 'data'
    #   - resource block: mode == 'managed'
    managed_resources = {r["address"]: r for r in resources if r["mode"] == "managed"}
    return managed_resources
