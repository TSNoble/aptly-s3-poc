import os

from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct

class AptlyS3PocStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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
            id="AptlyRepositoryReadOnlyGroup",
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
