from pathlib import Path

from aws_cdk import (
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct

from aws.constructs import (
    aws_s3_deployment as s3_deploy,
    aws_route53 as route53,
)

class AptlyRepository(Construct):
    """ An pair S3 Buckets which host apt packages managed via Aptly, and the public signing key."""

    def __init__(self, scope: Construct, id: str):
        super(AptlyRepository, self).__init__(scope, id)

        self.bucket = s3.Bucket(
            scope=self,
            id="Bucket",
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        s3_deploy.SingleFileBucketDeployment(
            scope=self,
            id="BucketIndexDeployment",
            destination_bucket=self.bucket,
            file=Path.cwd().absolute() / "config/index.html",
        )

    def grant_read_package(self, principal: iam.IGrantable):
        """ Grants a `principal` permission to read packages."""
        self.bucket.grant_read(
            principal,
            objects_key_pattern="dists/*",
        )
        self.bucket.grant_read(
            principal,
            objects_key_pattern="pool/*",
        )
    
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
                self.bucket.bucket_arn,
                f"{self.bucket.bucket_arn}/*"
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
                f"{self.bucket.bucket_arn}/public.pgp",
            ]
        )
        principal.add_to_policy(allow_update_key)
