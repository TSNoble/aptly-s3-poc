from aws_cdk import aws_iam as iam

from aptly_s3_poc.utils import verify_unset


class GitHubOIDCPrincipal(iam.OpenIdConnectPrincipal):
    """An OpenIdConnectPrincipal accessible to a GitHub runner in `environment` of `repo`."""

    def __init__(
        self,
        provider: iam.OpenIdConnectProvider,
        repo: str,
        environment: str,
        *args,
        **kwargs,
    ) -> None:
        verify_unset(kwargs, ["conditions"])
        issuer = "token.actions.githubusercontent.com"
        kwargs["conditions"] = {
            "StringEquals": {
                f"{issuer}:aud": "sts.amazonaws.com",
                f"{issuer}:sub": f"repo:{repo}:environment:{environment}",
            }
        }
        super(GitHubOIDCPrincipal, self).__init__(provider, *args, **kwargs)