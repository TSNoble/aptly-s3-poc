from aws_cdk import (
    aws_iam as iam,
)


class GitHubOIDCPrincipal(iam.OpenIdConnectPrincipal):
    """An OpenIdConnectPrincipal accessible to a GitHub runner in `environment` of `repo`."""

    def __init__(
        self,
        provider: iam.OpenIdConnectProvider,
        repository: str,
        environment: str,
        *args,
        **kwargs,
    ) -> None:
        issuer = "token.actions.githubusercontent.com"
        audience = "sts.amazonaws.com"
        kwargs["conditions"] = {
            "StringEquals": {
                f"{issuer}:aud": audience,
                f"{issuer}:sub": f"repo:{repository}:environment:{environment}",
            }
        }
        super(GitHubOIDCPrincipal, self).__init__(provider, *args, **kwargs)