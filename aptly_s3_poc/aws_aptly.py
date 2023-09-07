from pathlib import Path

from aws_cdk import (
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct

from aptly_s3_poc import (
    aws_s3_deployment as s3_deploy,
)

class AptlyRepository(Construct):
    """ An pair S3 Buckets which host apt packages managed via Aptly, and the public signing key."""

    def __init__(self, scope: Construct, id: str):
        super(AptlyRepository, self).__init__(scope, id)
        self.package_bucket = s3.Bucket(
            scope=self,
            id=f"PackageBucket",
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.key_bucket = s3.Bucket(
            scope=self,
            id=f"KeyBucket",
            website_index_document="index.html",
            auto_delete_objects=True,
            public_read_access=True,
            access_control=s3.BucketAccessControl.PUBLIC_READ,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        s3_deploy.SingleFileBucketDeployment(
            scope=self,
            id=f"KeyBucketIndexDeployment",
            destination_bucket=self.key_bucket,
            file=Path.cwd().absolute() / "index.html",
        )

    def grant_read_package(self, principal: iam.IGrantable):
        """ Grants a `principal` permission to read packages."""
        self.package_bucket.grant_read(principal)
    
    def grant_publish_package(self, principal: iam.IGrantable):
        """ Grants a `principal` permission to publish packages."""
        allow_publish = iam.PolicyStatement(
            sid="AllowPublishToAptlyRepository",
            actions=[
                "s3:DeleteObject",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:PutObject",
                "s3:PutObjectAcl",
            ],
            resources=[
                self.package_bucket.bucket_arn,
                f"{self.package_bucket.bucket_arn}/*"
            ]
        )
        principal.add_to_policy(allow_publish)

    def grant_update_key(self, principal: iam.IGrantable):
        """ Grants a `principal` permission to update the signing key."""
        allow_update_key = iam.PolicyStatement(
            sid="AllowUpdateAptlySigningKey",
            actions=[
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:PutObject",
            ],
            resources=[
                f"{self.key_bucket.bucket_arn}/public.pgp",
            ]
        )
        principal.add_to_policy(allow_update_key)