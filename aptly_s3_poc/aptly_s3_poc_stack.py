import os

from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct

from aptly_s3_poc.github_oidc_principal import GitHubOIDCPrincipal

class AptlyS3PocStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repository = s3.Bucket(
            scope=self,
            id="AptlyRepository",
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY
        )

        read_only_group = iam.Group(
            scope=self,
            id="AptlyRepositoryReadOnlyGroup"
        )

        repository.grant_read(read_only_group)

        read_only_role = iam.Role(
            scope=self,
            id="AptlyRepositoryReadOnlyRole",
            assumed_by=iam.AccountPrincipal("778015471639"),
            description="A role granting read-only access to the Aptly repository."
        )

        repository.grant_read(read_only_role)

        write_only_role = iam.Role(
            scope=self,
            id="AptlyRepositoryWriteOnlyRole",
            assumed_by=iam.AccountPrincipal("778015471639"),
            description="A role granting write-only access to the Aptly repository."
        )

        repository.grant_write(write_only_role)

        github_provider = iam.OpenIdConnectProvider(
            scope=self,
            id="GitHubOIDCProvider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"]
        )

        github_principal = GitHubOIDCPrincipal(
            provider=github_provider,
            repo="TSNoble/aptly-s3-poc",
            environment="Development",
        )

        write_only_role.grant_assume_role(github_principal)

