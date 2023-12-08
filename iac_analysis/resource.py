import logging

logger = logging.getLogger(__name__)


class ResourceTypes:
    AWS_S3_Bucket = "AWS::S3::Bucket"
    AWS_SQS_Queue = "AWS::SQS::Queue"
    AWS_Lambda_Function = "AWS::Lambda::Function"
    AWS_Lambda_EventSourceMapping = "AWS::Lambda::EventSourceMapping"
    AWS_SNS_Subscription = "AWS::SNS::Subscription"
    AWS_SNS_Topic = "AWS::SNS::Topic"
    AWS_S3_AccessPoint = "AWS::S3::AccessPoint"
    AWS_S3ObjectLambda_AccessPoint = "AWS::S3ObjectLambda::AccessPoint"

    AWS_S3_BucketPolicy = "AWS::S3::BucketPolicy"
    AWS_Lambda_Permission = "AWS::Lambda::Permission"
    AWS_SQS_QueuePolicy = "AWS::SQS::QueuePolicy"
    AWS_SNS_TopicPolicy = "AWS::SNS::TopicPolicy"
    AWS_IAM_Role = "AWS::IAM::Role"
    AWS_IAM_Policy = "AWS::IAM::Policy"
    AWS_CDK_Metadata = "AWS::CDK::Metadata"


class ResourceMetric:
    monthly_requests = "monthly_requests"


supported_resource_types = [
    ResourceTypes.AWS_S3_Bucket,
    ResourceTypes.AWS_SQS_Queue,
    ResourceTypes.AWS_Lambda_Function,
    ResourceTypes.AWS_Lambda_EventSourceMapping,
    ResourceTypes.AWS_SNS_Subscription,
    ResourceTypes.AWS_SNS_Topic,
    ResourceTypes.AWS_S3_AccessPoint,
    ResourceTypes.AWS_S3ObjectLambda_AccessPoint,
]

ignore_resource_types = [
    ResourceTypes.AWS_S3_BucketPolicy,
    ResourceTypes.AWS_Lambda_Permission,
    ResourceTypes.AWS_SQS_QueuePolicy,
    ResourceTypes.AWS_SNS_TopicPolicy,
    ResourceTypes.AWS_IAM_Role,
    ResourceTypes.AWS_IAM_Policy,
    ResourceTypes.AWS_CDK_Metadata,
]


class Resource:
    def __init__(self, name, resource_type, config):
        self.name = name
        self.resource_type = resource_type
        self.config = config
        self.incoming_edges = set()
        self.outgoing_edges = set()

    def __repr__(self):
        return self.name

    def __hash__(self):
        """
        Unique hash is the resource name. The __hash__ method is used
        for computing topological order using graphlib.
        """
        return hash(self.name)

    def add_incoming_edge(self, source):
        if source not in self.incoming_edges:
            self.incoming_edges.add(source)
        if self not in source.outgoing_edges:
            source.add_outgoing_edge(self)

    def add_outgoing_edge(self, destination):
        if destination not in self.outgoing_edges:
            self.outgoing_edges.add(destination)
        if self not in self.incoming_edges:
            destination.add_incoming_edge(self)

    @staticmethod
    def add_edge(source, destination):
        source.add_outgoing_edge(destination)
        destination.add_incoming_edge(source)

    def compute_edges(self, all_resources):
        match self.resource_type:
            case ResourceTypes.AWS_S3_Bucket:
                pass
            case ResourceTypes.AWS_SNS_Subscription:
                try:
                    endpoint = ref_or_getatt(self.config["Properties"]["Endpoint"])
                    self.add_outgoing_edge(all_resources[endpoint])
                    topic = ref_or_getatt(self.config["Properties"]["TopicArn"])
                    self.add_incoming_edge(all_resources[topic])
                except Exception:
                    logger.info(f"No endpoint or topic for {self.name}")
            case ResourceTypes.AWS_SNS_Topic:
                pass
            case ResourceTypes.AWS_Lambda_EventSourceMapping:
                # eventSource and lambdaFunction
                try:
                    eventSource = ref_or_getatt(
                        self.config["Properties"]["EventSourceArn"]
                    )
                    self.add_incoming_edge(all_resources[eventSource])
                    lambdaFunction = ref_or_getatt(
                        self.config["Properties"]["FunctionName"]
                    )
                    self.add_outgoing_edge(all_resources[lambdaFunction])
                except Exception:
                    logger.info(f"No eventSource or lambdaFunction for {self.name}")
            case ResourceTypes.AWS_Lambda_Function:
                try:
                    for _, envvar in self.config["Properties"]["Environment"][
                        "Variables"
                    ].items():
                        try:
                            x = ref_or_getatt(envvar)
                            self.add_outgoing_edge(all_resources[x])
                        except KeyError:
                            pass
                except Exception:
                    logger.info(f"No environment variables for {self.name}")

            case ResourceTypes.AWS_SQS_Queue:
                # deadLetterTarget
                try:
                    deadLetterTarget = ref_or_getatt(
                        self.config["Properties"]["RedrivePolicy"][
                            "deadLetterTargetArn"
                        ]
                    )
                    self.add_outgoing_edge(all_resources[deadLetterTarget])
                except Exception:
                    logger.info(f"No deadLetterTarget for {self.name}")
            case unknown_resource_type:
                logger.warn(
                    f"Encountered unhandled resource type ({unknown_resource_type}) when computing edges for {self.name}"
                )

    def compute_constraints(self, solver):
        match self.resource_type:
            case ResourceTypes.AWS_S3_Bucket:
                pass
            case ResourceTypes.AWS_Lambda_EventSourceMapping:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                solver.add_broadcast_equality_outgoing_constraints(
                    self, ResourceMetric.monthly_requests
                )
            case ResourceTypes.AWS_Lambda_Function:
                pass
            case ResourceTypes.AWS_SQS_Queue:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                for outn in self.outgoing_edges:
                    if (
                        outn.resource_type
                        == ResourceTypes.AWS_Lambda_EventSourceMapping
                    ):
                        solver.add(
                            solver.nv(self, ResourceMetric.monthly_requests)
                            == solver.ev(self, outn, ResourceMetric.monthly_requests)
                        )
            case unknown_resource_type:
                logger.warn(
                    f"Encountered unhandled resource type ({unknown_resource_type}) when computing constraints for {self.name}"
                )


def ref_or_getatt(config):
    try:
        return config["Ref"]
    except KeyError:
        return config["Fn::GetAtt"][0]
