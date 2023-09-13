from aws_cdk import (
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
)

from aws.constructs import (
    aws_cloudfront as cloudfront,
)


class HttpsS3Domain(route53.PublicHostedZone):

    def __init__(self, domain: str, bucket: s3.Bucket, *args, **kwargs):
        
        distribution = cloudfront.HttpsS3Distribution(
            scope=kwargs["scope"],
            id=f"{kwargs['id']}Distribution",
            bucket=bucket,
        )

        super(HttpsS3Domain, self).__init__(
            zone_name=domain,
            *args,
            **kwargs,
        )

        route53.ARecord(
            scope=kwargs["scope"],
            id=f"{kwargs['id']}DistributionARecord",
            zone=self,
            target=route53.RecordTarget.from_alias(
                alias_target=targets.CloudFrontTarget(
                    distribution=distribution,
                )
            )    
        )