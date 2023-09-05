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
        
        publisher_role = iam.Role(
            scope=self,
            id="AptlyRepositoryPublisherRole",
            assumed_by=github_principal,
            description="A role granting write-only access to the Aptly repository."
        )

        allow_publish_policy = iam.Policy(
            scope=self,
            id="AptlyRepositoryAllowPublishPolicy",
            statements=[
                iam.PolicyStatement(
                    sid="AllowPublishToAptlyRepository",
                    actions=[
                        "s3:DeleteObject",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:PutObject",
                        "s3:PutObjectAcl",
                    ],
                    resources=[
                        repository.bucket_arn,
                        repository.arn_for_objects(),
                    ]
                )
            ],
        )

        allow_publish_policy.attach_to_role(publisher_role)
