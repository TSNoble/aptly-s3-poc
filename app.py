#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk import (
    aws_iam as iam,
)

from aptly_s3_poc.aptly_s3_poc_stack import AptlyS3PocStack


app = cdk.App()

github_provider_arn = os.environ["AWS_GITHUB_PROVIDER_ARN"]

AptlyS3PocStack(
    scope=app,
    id="AptlyS3PocStack",
    github_provider_arn=github_provider_arn,
)

app.synth()
