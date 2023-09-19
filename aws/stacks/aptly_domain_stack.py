from aws_cdk import (
    Stack,
)
from constructs import Construct

from aws.constructs import (
    aws_route53 as route53,
)
from aws.stacks import (
  aptly_repository_stack,
)

class AptlyDomainStack(Stack):

    def __init__(self, scope: Construct, id: str, aptly_repository_stack: aptly_repository_stack.AptlyRepositoryStack, domain: str, **kwargs) -> None:
        
        super().__init__(scope, id, **kwargs)

        self.domain = route53.HttpsS3Domain(
            scope=self,
            id="Domain",
            domain=domain,
            bucket=aptly_repository_stack.repository.bucket,
        )
