from pathlib import Path

from aws_cdk import (
    aws_s3_deployment as s3_deploy,
)


class SingleFileBucketDeployment(s3_deploy.BucketDeployment):
    """Utility class which deploys a single file to a Bucket."""

    def __init__(self, file: Path, *args, **kwargs):
        file_asset = s3_deploy.Source.asset(
            path=str(file.parent),
            exclude=["**", ".*", f"!{file.name}"],
        )
        super(SingleFileBucketDeployment, self).__init__(
            *args,
            **kwargs,
            sources=[file_asset],
        )
