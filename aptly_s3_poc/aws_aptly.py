from aws_cdk import (
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct


class AptlyRepository(Construct):
    """ An S3 Bucket which hosts apt packaged managed via Aptly."""

    def __init__(self, scope: Construct, id: str):
        self.bucket = s3.Bucket(
            scope=self,
            id=f"f{self.id}Bucket",
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY
        )
        super.__init__(AptlyRepository, scope, id)

    def grant_read(self, principal: iam.IGrantable):
        """ Grants a `principal` permission to read packages."""
        self.bucket.grant_read(principal)
    
    def grant_publish(self, principal: iam.IGrantable):
        """ Grants a `principal` permission to publish packages."""
        allow_publish = iam.Policy(
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
                        self.bucket.bucket_arn,
                        f"{self.bucket.bucket_arn}/*"
                    ]
                )
            ],
        )
        principal.add_to_policy(allow_publish)