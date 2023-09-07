from aws_cdk import (
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct


class AptlyRepository(Construct):
    """ An pair S3 Buckets which host apt packages managed via Aptly, and the public signing key."""

    def __init__(self, scope: Construct, id: str):
        super(AptlyRepository, self).__init__(scope, id)
        self.package_bucket = s3.Bucket(
            scope=self,
            id=f"{id}Bucket",
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.key_bucket = s3.Bucket(
            scope=self,
            id=f"{id}KeyBucket",
            website_index_document="index.html",
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

    def grant_read(self, principal: iam.IGrantable):
        """ Grants a `principal` permission to read packages."""
        self.package_bucket.grant_read(principal)
        self.key_bucket.grant_read(principal)
    
    def grant_publish(self, principal: iam.IGrantable):
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