#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws.stacks.aptly_repository_stack import AptlyRepositoryStack


app = cdk.App()

github_branch = os.getenv("GITHUB_REF", default="")
github_provider_arn = os.environ["AWS_GITHUB_PROVIDER_ARN"]

AptlyRepositoryStack(
    scope=app,
    id=f"{github_branch}AptlyRepositoryStack",
    github_provider_arn=github_provider_arn,
    env=cdk.Environment(account="778015471639", region="us-east-1"),
)

app.synth()
