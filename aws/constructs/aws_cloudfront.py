from pathlib import Path

from aws_cdk import (
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_lambda as lambda_,
    aws_s3 as s3,
)


class HttpsS3Distribution(cloudfront.Distribution):

    def __init__(self, bucket: s3.Bucket, *args, **kwargs):
        
        auth_lambda = cloudfront.experimental.EdgeFunction(
            scope=kwargs["scope"],
            id=f"{kwargs['id']}HttpsAuthLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="https_auth.handler",
            code=lambda_.Code.from_asset(str(Path.cwd().absolute() / "aws/lambdas/auth")),
        )

        super(HttpsS3Distribution, self).__init__(
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    bucket=bucket,
                    custom_headers= {
                        "X-Aws-Deployment-Bucket-Name": bucket.bucket_name,
                    }
                ),
                edge_lambdas=[
                    cloudfront.EdgeLambda(
                        function_version=auth_lambda.current_version,
                        event_type=cloudfront.LambdaEdgeEventType.ORIGIN_REQUEST,
                    )
                ],
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
            ),
            *args,
            **kwargs,
        )