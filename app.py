#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws.stacks import (
    aptly_repository_stack as repository_stack,
    aptly_domain_stack as domain_stack,
)


app = cdk.App()

github_branch = os.getenv("GITHUB_REF", default="")
github_provider_arn = os.environ["AWS_GITHUB_PROVIDER_ARN"]
us_east_dev_account = env=cdk.Environment(account="778015471639", region="us-east-1")

repository = repository_stack.AptlyRepositoryStack(
    scope=app,
    id=f"{github_branch}AptlyRepositoryStack",
    github_provider_arn=github_provider_arn,
    env=us_east_dev_account,
)

domain = domain_stack.AptlyDomainStack(
    scope=app,
    id=f"{github_branch}AptlyDomainStack",
    aptly_repository_stack = repository,
    env=us_east_dev_account,
)

app.synth()
