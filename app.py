#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws.stacks import (
    aptly_repository_stack as repository_stack,
    aptly_domain_stack as domain_stack,
    github_permissions_stack as github_stack,
)


app = cdk.App()

github_branch = os.getenv("GITHUB_HEAD_REF", default="")
github_provider_arn = os.environ["AWS_GITHUB_PROVIDER_ARN"]
us_east_dev_account = env=cdk.Environment(account="778015471639", region="us-east-1")

repository = repository_stack.AptlyRepositoryStack(
    scope=app,
    id=f"{github_branch}AptlyRepositoryStack",
    env=us_east_dev_account,
)

domain = domain_stack.AptlyDomainStack(
    scope=app,
    id=f"{github_branch}AptlyDomainStack",
    aptly_repository_stack=repository,
    domain="dev.downloads.rivel.in",
    env=us_east_dev_account,
)

github = github_stack.GithubPermissionsStack(
    scope=app,
    id=f"{github_branch}AptlyGitHubStack",
    github_provider_arn=github_provider_arn,
    readers=[("TSNoble/aptly-s3-poc", "Test")],
    writers=[("TSNoble/aptly-s3-poc", "Publish")],
    key_managers=[("TSNoble/aptly-s3-poc", "KeyRotation")],
    env=us_east_dev_account,
)

app.synth()
