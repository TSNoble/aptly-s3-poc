from typing import (
  List,
  Tuple,
)

from aws_cdk import (
    Stack,
)
from constructs import Construct

from aws.stacks import (
  aptly_repository_stack,
)
from aws.constructs import (
  aws_github as github,
)

class GithubPermissionsStack(Stack):

    def __init__(
      self,
      scope: Construct,
      id: str,
      aptly_repository_stack: aptly_repository_stack.AptlyRepositoryStack,
      github_provider_arn: str,
      readers: List[Tuple[str]],
      publishers: List[Tuple[str]],
      key_managers: List[Tuple[str]],
      **kwargs
    )-> None:
        
        super().__init__(scope, id, **kwargs)

        github_provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            scope=self,
            id="ImportedGithubOIDCProvider",
            open_id_connect_provider_arn=github_provider_arn,
        )

        for reader in readers:
          repository, environment = reader
          principal = github.OIDCGitHubPrincipal(
            provider = github_provider,
            repository = repository,
            environment = environment,
          )
          aptly_repository_stack.read_only_role.grant_assume(principal)

      for publisher in publishers:
          repository, environment = publisher
          principal = github.OIDCGitHubPrincipal(
            provider = github_provider,
            repository = repository,
            environment = environment,
          )
          aptly_repository_stack.publisher_role.grant_assume(principal)

      for manager in key_managers:
        repository, environment = manager
        principal = github.OIDCGitHubPrincipal(
          provider = github_provider,
          repository = repository,
          environment = environment,
        )
        aptly_repository_stack.key_manager_role.grant_assume(principal)
