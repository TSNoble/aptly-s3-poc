#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aptly_s3_poc.stacks.aptly_repository_stack import AptlyRepositoryStack


app = cdk.App()

github_provider_arn = os.environ["AWS_GITHUB_PROVIDER_ARN"]

AptlyRepositoryStack(
    scope=app,
    id="AptlyRepositoryStack",
    github_provider_arn=github_provider_arn,
)

app.synth()
