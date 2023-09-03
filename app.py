#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk import (
    aws_iam as iam,
)

from aptly_s3_poc.aptly_s3_poc_stack import AptlyS3PocStack


app = cdk.App()
AptlyS3PocStack(app, "AptlyS3PocStack")
app.synth()
