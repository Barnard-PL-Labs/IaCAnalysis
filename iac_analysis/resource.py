import logging

logger = logging.getLogger(__name__)


class ResourceTypes:
    AWS_S3_Bucket = "AWS::S3::Bucket"
    AWS_SQS_Queue = "AWS::SQS::Queue"
    AWS_Lambda_Function = "AWS::Lambda::Function"
    AWS_Lambda_Alias = "AWS::Lambda::Alias"
    AWS_Lambda_EventSourceMapping = "AWS::Lambda::EventSourceMapping"
    AWS_Serverless_Function = "AWS::Serverless::Function"
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
    monthly_s3_object_created = "monthly_s3_object_created"
    monthly_s3_object_removed = "monthly_s3_object_removed"


supported_resource_types = [
    ResourceTypes.AWS_S3_Bucket,
    ResourceTypes.AWS_SQS_Queue,
    ResourceTypes.AWS_Lambda_Function,
    ResourceTypes.AWS_Lambda_Alias,
    ResourceTypes.AWS_Lambda_EventSourceMapping,
    ResourceTypes.AWS_Serverless_Function,
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

public_usage_metrics = {
    ResourceTypes.AWS_S3_Bucket: [
        ResourceMetric.monthly_s3_object_created,
        ResourceMetric.monthly_s3_object_removed,
    ],
    ResourceTypes.AWS_SQS_Queue: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_Lambda_Function: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_Serverless_Function: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_SNS_Topic: [ResourceMetric.monthly_requests],
}


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
                # LambdaConfigurations
                try:
                    lambdas = []
                    for lambdaConfiguration in self.config["Properties"][
                        "NotificationConfiguration"
                    ]["LambdaConfigurations"]:
                        if "Filter" in lambdaConfiguration:
                            logger.warn(
                                f"'Filter' is not supported in S3 NotificationConfiguration"
                            )
                        lambdas.append(ref_or_getatt(lambdaConfiguration["Function"]))
                    for l in lambdas:
                        self.add_outgoing_edge(all_resources[l])
                except:
                    logger.info(f"No LambdaConfigurations for {self.name}")
                # QueueConfigurations
                try:
                    queues = []
                    for queueConfiguration in self.config["Properties"][
                        "NotificationConfiguration"
                    ]["QueueConfigurations"]:
                        if "Filter" in queueConfiguration:
                            logger.warn(
                                f"'Filter' is not supported in S3 NotificationConfiguration"
                            )
                        queues.append(ref_or_getatt(queueConfiguration["Queue"]))
                    for q in queues:
                        self.add_outgoing_edge(all_resources[q])
                except:
                    logger.info(f"No QueueConfigurations for {self.name}")
                # TopicConfigurations
                try:
                    topics = []
                    for topicConfiguration in self.config["Properties"][
                        "NotificationConfiguration"
                    ]["TopicConfigurations"]:
                        if "Filter" in topicConfiguration:
                            logger.warn(
                                f"'Filter' is not supported in S3 NotificationConfiguration"
                            )
                        topics.append(ref_or_getatt(topicConfiguration["Topic"]))
                    for t in topics:
                        self.add_outgoing_edge(all_resources[t])
                except:
                    logger.info(f"No TopicConfigurations for {self.name}")
                # TODO: EventBridgeConfiguration
            case ResourceTypes.AWS_SNS_Subscription:
                try:
                    endpoint = ref_or_getatt(self.config["Properties"]["Endpoint"])
                    self.add_outgoing_edge(all_resources[endpoint])
                    topic = ref_or_getatt(self.config["Properties"]["TopicArn"])
                    self.add_incoming_edge(all_resources[topic])
                except:
                    logger.info(f"No endpoint or topic for {self.name}")
            case ResourceTypes.AWS_SNS_Topic:
                try:
                    for subscription in self.config["Properties"]["Subscription"]:
                        endpoint = ref_or_getatt(subscription["Endpoint"])
                        self.add_outgoing_edge(all_resources[endpoint])
                except:
                    logger.info(f"No endpoint for {self.name}")
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
                except:
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
                except:
                    logger.info(f"No environment variables for {self.name}")
            case ResourceTypes.AWS_Lambda_Alias:
                try:
                    lambdaFunction = ref_or_getatt(
                        self.config["Properties"]["FunctionName"]
                    )
                    self.add_outgoing_edge(all_resources[lambdaFunction])
                except:
                    logger.info(f"No environment variables for {self.name}")
            case ResourceTypes.AWS_Serverless_Function:
                try:
                    for _, envvar in self.config["Properties"]["Environment"][
                        "Variables"
                    ].items():
                        try:
                            x = ref_or_getatt(envvar)
                            self.add_outgoing_edge(all_resources[x])
                        except KeyError:
                            pass
                except:
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
                except:
                    logger.info(f"No deadLetterTarget for {self.name}")
            case unknown_resource_type:
                logger.warn(
                    f"Encountered unhandled resource type ({unknown_resource_type}) when computing edges for {self.name}"
                )

    def compute_constraints(self, solver, all_resources):
        match self.resource_type:
            case ResourceTypes.AWS_S3_Bucket:
                # > incoming constraints

                # > intrinsic constraints

                # > outgoing constraints
                # LambdaConfigurations
                try:
                    for lambdaConfiguration in self.config["Properties"][
                        "NotificationConfiguration"
                    ]["LambdaConfigurations"]:
                        match lambdaConfiguration["Event"]:
                            case "s3:ObjectCreated:*":
                                target_lambda = all_resources[
                                    ref_or_getatt(lambdaConfiguration["Function"])
                                ]
                                solver.add(
                                    solver.nv(
                                        self, ResourceMetric.monthly_s3_object_created
                                    )
                                    == solver.ev(
                                        self,
                                        target_lambda,
                                        ResourceMetric.monthly_requests,
                                    )
                                )
                            case "s3:ObjectRemoved:*":
                                target_lambda = all_resources[
                                    ref_or_getatt(lambdaConfiguration["Function"])
                                ]
                                solver.add(
                                    solver.nv(
                                        self, ResourceMetric.monthly_s3_object_removed
                                    )
                                    == solver.ev(
                                        self,
                                        target_lambda,
                                        ResourceMetric.monthly_requests,
                                    )
                                )
                except:
                    pass
                # QueueConfigurations
                try:
                    for queueConfiguration in self.config["Properties"][
                        "NotificationConfiguration"
                    ]["QueueConfigurations"]:
                        match queueConfiguration["Event"]:
                            case "s3:ObjectCreated:*":
                                target_queue = all_resources[
                                    ref_or_getatt(queueConfiguration["Queue"])
                                ]
                                solver.add(
                                    solver.nv(
                                        self, ResourceMetric.monthly_s3_object_created
                                    )
                                    == solver.ev(
                                        self,
                                        target_queue,
                                        ResourceMetric.monthly_requests,
                                    )
                                )
                            case "s3:ObjectRemoved:*":
                                target_queue = all_resources[
                                    ref_or_getatt(lambdaConfiguration["Queue"])
                                ]
                                solver.add(
                                    solver.nv(
                                        self, ResourceMetric.monthly_s3_object_removed
                                    )
                                    == solver.ev(
                                        self,
                                        target_queue,
                                        ResourceMetric.monthly_requests,
                                    )
                                )
                except:
                    pass
                # TopicConfigurations
                try:
                    for topicConfiguration in self.config["Properties"][
                        "NotificationConfiguration"
                    ]["TopicConfigurations"]:
                        match topicConfiguration["Event"]:
                            case "s3:ObjectCreated:*":
                                target_topic = all_resources[
                                    ref_or_getatt(topicConfiguration["Topic"])
                                ]
                                solver.add(
                                    solver.nv(
                                        self, ResourceMetric.monthly_s3_object_created
                                    )
                                    == solver.ev(
                                        self,
                                        target_topic,
                                        ResourceMetric.monthly_requests,
                                    )
                                )
                            case "s3:ObjectRemoved:*":
                                target_topic = all_resources[
                                    ref_or_getatt(topicConfiguration["Topic"])
                                ]
                                solver.add(
                                    solver.nv(
                                        self, ResourceMetric.monthly_s3_object_removed
                                    )
                                    == solver.ev(
                                        self,
                                        target_topic,
                                        ResourceMetric.monthly_requests,
                                    )
                                )
                except:
                    pass
            case ResourceTypes.AWS_Lambda_EventSourceMapping:
                # > incoming constraints
                # from eventSource
                assert len(self.incoming_edges) == 1
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                # to lambdaFunction
                assert len(self.outgoing_edges) == 1
                outgoing = list(self.outgoing_edges)[0]
                solver.add(
                    solver.nv(self, ResourceMetric.monthly_requests)
                    == solver.ev(self, outgoing, ResourceMetric.monthly_requests)
                )
            case ResourceTypes.AWS_Lambda_Function:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
            case ResourceTypes.AWS_Lambda_Alias:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                assert len(self.outgoing_edges) == 1
                outgoing = list(self.outgoing_edges)[0]
                solver.add(
                    solver.nv(self, ResourceMetric.monthly_requests)
                    == solver.ev(self, outgoing, ResourceMetric.monthly_requests)
                )
            case ResourceTypes.AWS_Serverless_Function:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
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
            case ResourceTypes.AWS_SNS_Topic:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                for outn in self.outgoing_edges:
                    solver.add(
                        solver.nv(self, ResourceMetric.monthly_requests)
                        == solver.ev(self, outn, ResourceMetric.monthly_requests)
                    )
            case ResourceTypes.AWS_SNS_Subscription:
                # > incoming constraints
                assert len(self.incoming_edges) == 1
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                assert len(self.outgoing_edges) == 1
                outgoing = list(self.outgoing_edges)[0]
                solver.add(
                    solver.nv(self, ResourceMetric.monthly_requests)
                    == solver.ev(self, outgoing, ResourceMetric.monthly_requests)
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
