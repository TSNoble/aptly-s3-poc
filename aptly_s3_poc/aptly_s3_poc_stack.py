from aws_cdk import (
    Stack,
    CfnOutput,
    aws_iam as iam,
)
from constructs import Construct

from aptly_s3_poc import (
    aws_aptly as aptly,
    aws_github as github
)

class AptlyS3PocStack(Stack):

    def __init__(self, scope: Construct, id: str, github_provider_arn: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        repository = aptly.AptlyRepository(
            scope=self,
            id="AptlyRepository",
        )

        CfnOutput(
            scope=self,
            id="AptlyRepositoryBucketName",
            value=f"s3:{repository.bucket.bucket_name}:.",
        )

        github_provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            scope=self,
            id="ImportedGithubOIDCProvider",
            open_id_connect_provider_arn=github_provider_arn,
        )

        github_principal = github.GitHubOIDCPrincipal(
            provider=github_provider,
            repository="TSNoble/aptly-s3-poc",
            environment="Publish",
        )

        read_only_group = iam.Group(
            scope=self,
            id="AptlyRepositoryReadOnlyGroup",
        )

        repository.grant_read(read_only_group)

        read_only_role = iam.Role(
            scope=self,
            id="AptlyRepositoryReadOnlyRole",
            assumed_by=github_principal,
            description="A role granting read-only access to the Aptly repository."
        )

        repository.grant_read(read_only_role)
        
        publisher_role = iam.Role(
            scope=self,
            id="AptlyRepositoryPublisherRole",
            assumed_by=github_principal,
            description="A role granting write-only access to the Aptly repository."
        )

        repository.grant_publish(publisher_role)

        CfnOutput(
            scope=self,
            id="AptlyRepositoryPublisherRoleArn",
            value=publisher_role.role_arn,
        )

