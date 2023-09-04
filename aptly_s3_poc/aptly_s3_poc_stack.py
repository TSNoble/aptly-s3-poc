import os

from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct

class AptlyS3PocStack(Stack):

    def __init__(self, scope: Construct, id: str, github_provider_arn: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        repository = s3.Bucket(
            scope=self,
            id="AptlyRepository",
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY
        )

        github_provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            scope=self,
            id="ImportedGithubOIDCProvider",
            open_id_connect_provider_arn=github_provider_arn,
        )

        github_principal = iam.OpenIdConnectPrincipal(
            open_id_connect_provider=github_provider,
            conditions={
                "StringEquals": {
                    f"token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    f"token.actions.githubusercontent.com:sub": "repo:TSNoble/aptly-s3-poc:environment:Publish",
                }
            },
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
        
        write_only_role = iam.Role(
            scope=self,
            id="AptlyRepositoryWriteOnlyRole",
            assumed_by=github_principal,
            description="A role granting write-only access to the Aptly repository."
        )

        repository.grant_write(write_only_role)
