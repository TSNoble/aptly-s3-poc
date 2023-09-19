from aws_cdk import (
    Stack,
    CfnOutput,
    aws_iam as iam,
)
from constructs import Construct

from aws.constructs import (
    aws_aptly as aptly,
    aws_github as github
)

class AptlyRepositoryStack(Stack):

    def __init__(self, scope: Construct, id: str, github_provider_arn: str, **kwargs) -> None:
        
        super().__init__(scope, id, **kwargs)

        self.repository = aptly.AptlyRepository(
            scope=self,
            id="AptlyRepository",
        )

        CfnOutput(
            scope=self,
            id="BucketName",
            value=self.repository.bucket.bucket_name,
        )

        github_provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            scope=self,
            id="ImportedGithubOIDCProvider",
            open_id_connect_provider_arn=github_provider_arn,
        )

        github_publisher_principal = github.GitHubOIDCPrincipal(
            provider=github_provider,
            repository="TSNoble/aptly-s3-poc",
            environment="Publish",
        )

        self.read_only_group = iam.Group(
            scope=self,
            id="ReadOnlyGroup",
        )

        repository.grant_read_package(read_only_group)

        self.read_only_role = iam.Role(
            scope=self,
            id="ReadOnlyRole",
            assumed_by=github_publisher_principal,
            description="A role granting read-only access to the Aptly repository."
        )

        repository.grant_read_package(read_only_role)
        
        self.publisher_role = iam.Role(
            scope=self,
            id="PublisherRole",
            assumed_by=github_publisher_principal,
            description="A role granting write-only access to the Aptly repository."
        )

        repository.grant_publish_package(publisher_role)

        github_key_manager_principal = github.GitHubOIDCPrincipal(
            provider=github_provider,
            repository="TSNoble/aptly-s3-poc",
            environment="KeyRotation",
        )

        self.key_manager_role = iam.Role(
            scope=self,
            id="KeyManagerRole",
            assumed_by=github_key_manager_principal,
            description="A role granting signing key update permissions to the Aptly repository."
        )

        CfnOutput(
            scope=self,
            id="PublisherRoleArn",
            value=publisher_role.role_arn,
        )

        repository.grant_update_key(self.key_manager_role)

        CfnOutput(
            scope=self,
            id="KeyManagerRoleArn",
            value=self.key_manager_role.role_arn,
        )
