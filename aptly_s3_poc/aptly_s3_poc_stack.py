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
            id="AptlyRepositoryPackageBucketName",
            value=repository.package_bucket.bucket_name,
        )

        CfnOutput(
            scope=self,
            id="AptlyRepositoryPublicKeyUrl",
            value=f"{repository.key_bucket.bucket_website_domain_name}/public.pgp",
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

        read_only_group = iam.Group(
            scope=self,
            id="AptlyRepositoryReadOnlyGroup",
        )

        repository.grant_read_package(read_only_group)

        read_only_role = iam.Role(
            scope=self,
            id="AptlyRepositoryReadOnlyRole",
            assumed_by=github_publisher_principal,
            description="A role granting read-only access to the Aptly repository."
        )

        repository.grant_read_package(read_only_role)
        
        publisher_role = iam.Role(
            scope=self,
            id="AptlyRepositoryPublisherRole",
            assumed_by=github_principal,
            description="A role granting write-only access to the Aptly repository."
        )

        repository.grant_publish_package(publisher_role)

        github_key_manager_principal = github.GitHubOIDCPrincipal(
            provider=github_provider,
            repository="TSNoble/aptly-s3-poc",
            environment="KeyRotation",
        )

        key_manager_role = iam.Role(
            scope=self,
            id="AptlyRepositoryKeyManagerRole",
            assumed_by=github_key_manager_principal,
            description="A role granting signing key update permissions to the Aptly repository."
        )

        CfnOutput(
            scope=self,
            id="AptlyRepositoryPublisherRoleArn",
            value=publisher_role.role_arn,
        )

        repository.grant_update_key(key_manager_role)

        CfnOutput(
            scope=self,
            id="AptlyRepositoryKeyManagerRoleArn",
            value=key_manager_role.role_arn,
        )