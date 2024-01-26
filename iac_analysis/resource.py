import logging
from iac_analysis.solver import Implies

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
    AWS_DynamoDB_Table = "AWS::DynamoDB::Table"
    AWS_ApiGateway_RestApi = "AWS::ApiGateway::RestApi"
    AWS_ApiGateway_Resource = "AWS::ApiGateway::Resource"
    AWS_ApiGateway_Method = "AWS::ApiGateway::Method"

    AWS_ApiGateway_Deployment = "AWS::ApiGateway::Deployment"
    AWS_S3_BucketPolicy = "AWS::S3::BucketPolicy"
    AWS_Lambda_Permission = "AWS::Lambda::Permission"
    AWS_SQS_QueuePolicy = "AWS::SQS::QueuePolicy"
    AWS_SNS_TopicPolicy = "AWS::SNS::TopicPolicy"
    AWS_IAM_Role = "AWS::IAM::Role"
    AWS_IAM_Policy = "AWS::IAM::Policy"
    AWS_IAM_AccessKey = "AWS::IAM::AccessKey"
    AWS_IAM_Group = "AWS::IAM::Group"
    AWS_IAM_GroupPolicy = "AWS::IAM::GroupPolicy"
    AWS_IAM_InstanceProfile = "AWS::IAM::InstanceProfile"
    AWS_IAM_ManagedPolicy = "AWS::IAM::ManagedPolicy"
    AWS_IAM_OIDCProvider = "AWS::IAM::OIDCProvider"
    AWS_IAM_RolePolicy = "AWS::IAM::RolePolicy"
    AWS_IAM_SAMLProvider = "AWS::IAM::SAMLProvider"
    AWS_IAM_ServerCertificate = "AWS::IAM::ServerCertificate"
    AWS_IAM_ServiceLinkedRole = "AWS::IAM::ServiceLinkedRole"
    AWS_IAM_User = "AWS::IAM::User"
    AWS_IAM_UserPolicy = "AWS::IAM::UserPolicy"
    AWS_IAM_UserToGroupAddition = "AWS::IAM::UserToGroupAddition"
    AWS_IAM_VirtualMFADevice = "AWS::IAM::VirtualMFADevice"
    AWS_CDK_Metadata = "AWS::CDK::Metadata"


class ResourceMetric:
    monthly_requests = "monthly_requests"
    monthly_sqs_billing_requests = "monthly_sqs_billing_requests"
    monthly_s3_object_created = "monthly_s3_object_created"
    monthly_s3_object_removed = "monthly_s3_object_removed"
    monthly_dynamodb_r = "monthly_dynamodb_r"
    monthly_dynamodb_w = "monthly_dynamodb_w"
    monthly_dynamodb_rw = "monthly_dynamodb_rw"
    monthly_apigateway_resource_requests = "monthly_apigateway_resoure_requests"
    monthly_apigateway_resource_GETs = "monthly_apigateway_resource_GETs"
    monthly_apigateway_resource_POSTs = "monthly_apigateway_resource_POSTs"
    monthly_apigateway_resource_PUTs = "monthly_apigateway_resource_PUTs"
    monthly_apigateway_resource_DELETEs = "monthly_apigateway_resource_DELETEs"
    monthly_apigateway_resource_OPTIONSs = "monthly_apigateway_resource_OPTIONSs"
    monthly_apigateway_resource_PATCHs = "monthly_apigateway_resource_PATCHs"
    monthly_apigateway_resource_HEADs = "monthly_apigateway_resource_HEADs"


supported_resource_types = [
    ResourceTypes.AWS_S3_Bucket,
    ResourceTypes.AWS_SQS_Queue,
    ResourceTypes.AWS_Lambda_Function,
    ResourceTypes.AWS_Lambda_Alias,
    ResourceTypes.AWS_Lambda_EventSourceMapping,
    ResourceTypes.AWS_Serverless_Function,
    ResourceTypes.AWS_SNS_Subscription,
    ResourceTypes.AWS_SNS_Topic,
    ResourceTypes.AWS_DynamoDB_Table,
    ResourceTypes.AWS_ApiGateway_RestApi,
    ResourceTypes.AWS_ApiGateway_Resource,
    ResourceTypes.AWS_ApiGateway_Method,
]

ignore_resource_types = [
    ResourceTypes.AWS_S3_BucketPolicy,
    ResourceTypes.AWS_Lambda_Permission,
    ResourceTypes.AWS_SQS_QueuePolicy,
    ResourceTypes.AWS_SNS_TopicPolicy,
    ResourceTypes.AWS_IAM_Role,
    ResourceTypes.AWS_IAM_Policy,
    ResourceTypes.AWS_IAM_AccessKey,
    ResourceTypes.AWS_IAM_Group,
    ResourceTypes.AWS_IAM_GroupPolicy,
    ResourceTypes.AWS_IAM_InstanceProfile,
    ResourceTypes.AWS_IAM_ManagedPolicy,
    ResourceTypes.AWS_IAM_OIDCProvider,
    ResourceTypes.AWS_IAM_RolePolicy,
    ResourceTypes.AWS_IAM_SAMLProvider,
    ResourceTypes.AWS_IAM_ServerCertificate,
    ResourceTypes.AWS_IAM_ServiceLinkedRole,
    ResourceTypes.AWS_IAM_User,
    ResourceTypes.AWS_IAM_UserPolicy,
    ResourceTypes.AWS_IAM_UserToGroupAddition,
    ResourceTypes.AWS_IAM_VirtualMFADevice,
    ResourceTypes.AWS_CDK_Metadata,
    ResourceTypes.AWS_ApiGateway_Deployment,
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
    ResourceTypes.AWS_DynamoDB_Table: [
        ResourceMetric.monthly_dynamodb_r,
        ResourceMetric.monthly_dynamodb_w,
        ResourceMetric.monthly_dynamodb_rw,
    ],
    ResourceTypes.AWS_ApiGateway_Resource: [
        ResourceMetric.monthly_requests,
        ResourceMetric.monthly_apigateway_resource_GETs,
        ResourceMetric.monthly_apigateway_resource_POSTs,
        ResourceMetric.monthly_apigateway_resource_PUTs,
        ResourceMetric.monthly_apigateway_resource_DELETEs,
        ResourceMetric.monthly_apigateway_resource_OPTIONSs,
        ResourceMetric.monthly_apigateway_resource_PATCHs,
        ResourceMetric.monthly_apigateway_resource_HEADs,
    ],
}

metrics = {
    ResourceTypes.AWS_S3_Bucket: [
        ResourceMetric.monthly_s3_object_created,
        ResourceMetric.monthly_s3_object_removed,
    ],
    ResourceTypes.AWS_SQS_Queue: [
        ResourceMetric.monthly_requests,
        ResourceMetric.monthly_sqs_billing_requests,
    ],
    ResourceTypes.AWS_Lambda_Function: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_Serverless_Function: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_SNS_Topic: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_DynamoDB_Table: [
        ResourceMetric.monthly_dynamodb_r,
        ResourceMetric.monthly_dynamodb_w,
        ResourceMetric.monthly_dynamodb_rw,
    ],
    ResourceTypes.AWS_Lambda_Alias: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_Lambda_EventSourceMapping: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_SNS_Subscription: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_SNS_Topic: [ResourceMetric.monthly_requests],
    ResourceTypes.AWS_ApiGateway_RestApi: [],
    ResourceTypes.AWS_ApiGateway_Resource: [
        ResourceMetric.monthly_requests,
        ResourceMetric.monthly_apigateway_resource_GETs,
        ResourceMetric.monthly_apigateway_resource_POSTs,
        ResourceMetric.monthly_apigateway_resource_PUTs,
        ResourceMetric.monthly_apigateway_resource_DELETEs,
        ResourceMetric.monthly_apigateway_resource_OPTIONSs,
        ResourceMetric.monthly_apigateway_resource_PATCHs,
        ResourceMetric.monthly_apigateway_resource_HEADs,
    ],
    ResourceTypes.AWS_ApiGateway_Method: [ResourceMetric.monthly_requests],
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
                        lambdas.append(
                            try_find_occurrence(
                                all_resources, lambdaConfiguration["Function"]
                            )
                        )
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
                        queues.append(
                            try_find_occurrence(
                                all_resources, queueConfiguration["Queue"]
                            )
                        )
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
                        topics.append(
                            try_find_occurrence(
                                all_resources, topicConfiguration["Topic"]
                            )
                        )
                    for t in topics:
                        self.add_outgoing_edge(all_resources[t])
                except:
                    logger.info(f"No TopicConfigurations for {self.name}")
                # TODO: EventBridgeConfiguration
            case ResourceTypes.AWS_SNS_Subscription:
                try:
                    endpoint = try_find_occurrence(
                        all_resources, self.config["Properties"]["Endpoint"]
                    )
                    self.add_outgoing_edge(all_resources[endpoint])
                except:
                    logger.info(f"no endpoint for {self.name}")

                try:
                    topic = try_find_occurrence(
                        all_resources, self.config["Properties"]["TopicArn"]
                    )
                    self.add_incoming_edge(all_resources[topic])
                except:
                    logger.info(f"no topic for {self.name}")
            case ResourceTypes.AWS_SNS_Topic:
                try:
                    for subscription in self.config["Properties"]["Subscription"]:
                        endpoint = try_find_occurrence(
                            all_resources, subscription["Endpoint"]
                        )
                        self.add_outgoing_edge(all_resources[endpoint])
                except:
                    logger.info(f"No endpoint for {self.name}")
            case ResourceTypes.AWS_Lambda_EventSourceMapping:
                # eventSource and lambdaFunction
                try:
                    eventSource = try_find_occurrence(
                        all_resources, self.config["Properties"]["EventSourceArn"]
                    )
                    self.add_incoming_edge(all_resources[eventSource])
                except:
                    logger.info(f"No eventSource for {self.name}")
                try:
                    lambdaFunction = try_find_occurrence(
                        all_resources, self.config["Properties"]["FunctionName"]
                    )
                    self.add_outgoing_edge(all_resources[lambdaFunction])
                except:
                    logger.info(f"No lambdaFunction for {self.name}")
            case ResourceTypes.AWS_Lambda_Function:
                try:
                    for _, envvar in self.config["Properties"]["Environment"][
                        "Variables"
                    ].items():
                        try:
                            x = try_find_occurrence(all_resources, envvar)
                            self.add_outgoing_edge(all_resources[x])
                        except KeyError:
                            pass
                except:
                    logger.info(f"No environment variables for {self.name}")
            case ResourceTypes.AWS_Lambda_Alias:
                try:
                    lambdaFunction = try_find_occurrence(
                        all_resources, self.config["Properties"]["FunctionName"]
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
                            x = try_find_occurrence(all_resources, envvar)
                            self.add_outgoing_edge(all_resources[x])
                        except KeyError:
                            pass
                except:
                    logger.info(f"No environment variables for {self.name}")

            case ResourceTypes.AWS_SQS_Queue:
                # deadLetterTarget
                try:
                    deadLetterTarget = try_find_occurrence(
                        all_resources,
                        self.config["Properties"]["RedrivePolicy"][
                            "deadLetterTargetArn"
                        ],
                    )
                    self.add_outgoing_edge(all_resources[deadLetterTarget])
                except:
                    logger.info(f"No deadLetterTarget for {self.name}")
            case ResourceTypes.AWS_ApiGateway_RestApi:
                pass
            case ResourceTypes.AWS_ApiGateway_Resource:
                try:
                    parent = try_find_occurrence(
                        all_resources, self.config["Properties"]["ParentId"]
                    )
                    restApi = try_find_occurrence(
                        all_resources, self.config["Properties"]["RestApiId"]
                    )
                    self.add_outgoing_edge(all_resources[parent])
                except:
                    logger.info(f"No ParentId or RestApiId for {self.name}")
            case ResourceTypes.AWS_ApiGateway_Method:
                try:
                    resource = try_find_occurrence(
                        all_resources, self.config["Properties"]["ResourceId"]
                    )
                    restApi = try_find_occurrence(
                        all_resources, self.config["Properties"]["RestApiId"]
                    )
                    self.add_incoming_edge(all_resources[resource])
                except:
                    logger.info(f"No ResourceId or RestApiId for {self.name}")
                try:
                    integration = try_find_occurrence(
                        all_resources,
                        self.config["Properties"]["Integration"]["Uri"],
                    )
                    self.add_outgoing_edge(all_resources[integration])
                except:
                    logger.info(f"No Integration for {self.name}")
            case ResourceTypes.AWS_DynamoDB_Table:
                pass
            case unknown_resource_type:
                logger.warn(
                    f"Encountered unhandled resource type ({unknown_resource_type}) when computing edges for {self.name}"
                )

    def compute_constraints(self, solver, all_resources, custom_generator=None):
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
                                    try_find_occurrence(
                                        all_resources, lambdaConfiguration["Function"]
                                    )
                                ]
                                solver.add_outgoing(
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
                                    try_find_occurrence(
                                        all_resources, lambdaConfiguration["Function"]
                                    )
                                ]
                                solver.add_outgoing(
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
                                    try_find_occurrence(
                                        all_resources, queueConfiguration["Queue"]
                                    )
                                ]
                                solver.add_outgoing(
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
                                    try_find_occurrence(
                                        all_resources, lambdaConfiguration["Queue"]
                                    )
                                ]
                                solver.add_outgoing(
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
                                    try_find_occurrence(
                                        all_resources, topicConfiguration["Topic"]
                                    )
                                ]
                                solver.add_outgoing(
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
                                    try_find_occurrence(
                                        all_resources, topicConfiguration["Topic"]
                                    )
                                ]
                                solver.add_outgoing(
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
                # assert len(self.incoming_edges) == 1
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                # to lambdaFunction
                # assert len(self.outgoing_edges) == 1
                outgoing = list(self.outgoing_edges)[0]
                solver.add_outgoing(
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
                solver.add_outgoing(
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
                solver.add_intrinsic(
                    solver.nv(self, ResourceMetric.monthly_requests)
                    == solver.nv(self, ResourceMetric.monthly_sqs_billing_requests) * 3
                )

                # > outgoing constraints
                for outn in self.outgoing_edges:
                    if (
                        outn.resource_type
                        == ResourceTypes.AWS_Lambda_EventSourceMapping
                    ):
                        if (
                            "Properties" in self.config
                            and "FifoQueue" in self.config["Properties"]
                            and "ContentBasedDeduplication" in self.config["Properties"]
                            and self.config["Properties"]["FifoQueue"]
                            and self.config["Properties"]["ContentBasedDeduplication"]
                        ):
                            solver.add_outgoing(
                                solver.nv(self, ResourceMetric.monthly_requests)
                                >= solver.ev(
                                    self, outn, ResourceMetric.monthly_requests
                                )
                            )
                            solver.add_outgoing(
                                Implies(
                                    solver.nv(self, ResourceMetric.monthly_requests)
                                    > 0,
                                    solver.ev(
                                        self, outn, ResourceMetric.monthly_requests
                                    )
                                    > 0,
                                )
                            )
                        else:
                            solver.add_outgoing(
                                solver.nv(self, ResourceMetric.monthly_requests)
                                == solver.ev(
                                    self, outn, ResourceMetric.monthly_requests
                                )
                            )
            case ResourceTypes.AWS_SNS_Topic:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                for outn in self.outgoing_edges:
                    solver.add_outgoing(
                        solver.nv(self, ResourceMetric.monthly_requests)
                        == solver.ev(self, outn, ResourceMetric.monthly_requests)
                    )
            case ResourceTypes.AWS_SNS_Subscription:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                if len(self.outgoing_edges) > 0:
                    outgoing = list(self.outgoing_edges)[0]
                    solver.add_outgoing(
                        solver.nv(self, ResourceMetric.monthly_requests)
                        == solver.ev(self, outgoing, ResourceMetric.monthly_requests)
                    )

            case ResourceTypes.AWS_DynamoDB_Table:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_dynamodb_r
                )
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_dynamodb_w
                )

                # > intrinsic constraints
                solver.add_intrinsic(
                    solver.nv(self, ResourceMetric.monthly_dynamodb_rw)
                    == solver.nv(self, ResourceMetric.monthly_dynamodb_r)
                    + solver.nv(self, ResourceMetric.monthly_dynamodb_w)
                )

                # > outgoing constraints
            case ResourceTypes.AWS_ApiGateway_Resource:
                # > incoming constraints

                # > intrinsic constraints
                solver.add_intrinsic(
                    solver.nv(self, ResourceMetric.monthly_requests)
                    == solver.nv(self, ResourceMetric.monthly_apigateway_resource_GETs)
                    + solver.nv(self, ResourceMetric.monthly_apigateway_resource_POSTs)
                    + solver.nv(self, ResourceMetric.monthly_apigateway_resource_PUTs)
                    + solver.nv(
                        self, ResourceMetric.monthly_apigateway_resource_DELETEs
                    )
                    + solver.nv(
                        self, ResourceMetric.monthly_apigateway_resource_OPTIONSs
                    )
                    + solver.nv(self, ResourceMetric.monthly_apigateway_resource_PATCHs)
                    + solver.nv(self, ResourceMetric.monthly_apigateway_resource_HEADs)
                )

                # > outgoing constraints
                for outn in self.outgoing_edges:
                    if outn.resource_type == ResourceTypes.AWS_ApiGateway_Method:
                        metric = ResourceMetric.monthly_apigateway_resource_GETs
                        method = outn.config["Properties"]["HttpMethod"]
                        if method == "GET":
                            metric = ResourceMetric.monthly_apigateway_resource_GETs
                        elif method == "POST":
                            metric = ResourceMetric.monthly_apigateway_resource_POSTs
                        elif method == "PUT":
                            metric = ResourceMetric.monthly_apigateway_resource_PUTs
                        elif method == "DELETE":
                            metric = ResourceMetric.monthly_apigateway_resource_DELETEs
                        elif method == "OPTIONS":
                            metric = ResourceMetric.monthly_apigateway_resource_OPTIONSs
                        elif method == "PATCH":
                            metric = ResourceMetric.monthly_apigateway_resource_PATCHs
                        elif method == "HEAD":
                            metric = ResourceMetric.monthly_apigateway_resource_HEADs
                        elif method == "ANY":
                            metric = ResourceMetric.monthly_requests
                        else:
                            raise Exception("Unknown HTTP Method")

                        solver.add_outgoing(
                            solver.nv(self, metric)
                            == solver.ev(self, outn, ResourceMetric.monthly_requests)
                        )
            case ResourceTypes.AWS_ApiGateway_Method:
                # > incoming constraints
                solver.add_aggregate_incoming_constraint(
                    self, ResourceMetric.monthly_requests
                )

                # > intrinsic constraints

                # > outgoing constraints
                for outn in self.outgoing_edges:
                    solver.add_outgoing(
                        solver.nv(self, ResourceMetric.monthly_requests)
                        == solver.ev(self, outn, ResourceMetric.monthly_requests)
                    )

            case unknown_resource_type:
                logger.warn(
                    f"Encountered unhandled resource type ({unknown_resource_type}) when computing constraints for {self.name}"
                )

        if custom_generator:
            custom_generator(self, solver, all_resources)


def try_find_occurrence(all_resources, config):
    try:
        return config["Ref"]
    except KeyError:
        try:
            return config["Fn::GetAtt"][0]
        except KeyError:
            s = config["Fn::Sub"]
            for r in all_resources.values():
                if f"${{{r.name}" in s:
                    return r.name
            return None
