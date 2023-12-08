import logging

logger = logging.getLogger(__name__)


class ResourceTypes:
    AWS_S3_Bucket = "AWS::S3::Bucket"
    AWS_SQS_Queue = "AWS::SQS::Queue"
    AWS_Lambda_Function = "AWS::Lambda::Function"
    AWS_Lambda_EventSourceMapping = "AWS::Lambda::EventSourceMapping"


supported_resource_types = [
    ResourceTypes.AWS_S3_Bucket,
    ResourceTypes.AWS_SQS_Queue,
    ResourceTypes.AWS_Lambda_Function,
    ResourceTypes.AWS_Lambda_EventSourceMapping,
]

ignore_resource_types = []


class Resource:
    def __init__(self, name, resource_type, config):
        self.name = name
        self.resource_type = resource_type
        self.config = config
        self.incoming_edges = set()
        self.outgoing_edges = set()

    def __repr__(self):
        return f"<{self.name} ({self.resource_type})>"

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
            case ResourceTypes.AWS_Lambda_EventSourceMapping:
                try:
                    eventSource = self.config["Properties"]["EventSourceArn"][
                        "Fn::GetAtt"
                    ][0]
                    self.add_incoming_edge(all_resources[eventSource])
                    lambdaFunction = self.config["Properties"]["FunctionName"]["Ref"]
                    self.add_outgoing_edge(all_resources[lambdaFunction])
                except KeyError:
                    logger.info(f"KeyError when computing edges for {self.name}")
            case ResourceTypes.AWS_Lambda_Function:
                pass
            case ResourceTypes.AWS_SQS_Queue:
                pass
            case unknown_resource_type:
                logger.warn(
                    f"Encountered unhandled resource type ({unknown_resource_type}) when computing edges for {self.name}"
                )

    def compute_constraints(self, solver):
        match self.resource_type:
            case ResourceTypes.AWS_S3_Bucket:
                pass
            case ResourceTypes.AWS_Lambda_EventSourceMapping:
                pass
            case ResourceTypes.AWS_Lambda_Function:
                pass
            case ResourceTypes.AWS_SQS_Queue:
                pass
            case unknown_resource_type:
                logger.warn(
                    f"Encountered unhandled resource type ({unknown_resource_type}) when computing constraints for {self.name}"
                )
