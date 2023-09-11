import base64

import requests
from nacl import (
    encoding,
    public,
)
from invoke import (
    task,
    context,
)


@task
def create_github_secret(c: context.Context, repo: str, environment: str, token: str, name: str, value: str):
    secrets_url = f"https://api.github.com/repositories/{repo}/environments/{environment}/secrets"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    key_response = requests.get(
        url=f"{secrets_url}/public-key",
        headers=headers,
    )
    public_key = public.PublicKey(key_response.json()["key"].encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted_value = sealed_box.encrypt(value.encode("utf-8"))
    encoded_value = base64.b64encode(encrypted_value).decode("utf-8")
    secret_response = requests.put(
        url=f"{secrets_url}/{name}",
        headers=headers,
        json={
            "encrypted_value": encoded_value,
            "key_id": key_response.json()["key_id"],
        }
    )