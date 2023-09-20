import os

import pytest
import boto3


def test_unauthenticated_user_cannot_access_public_key():
    s3 = boto3.client("s3")
    bucket = os.environ["AWS_APTLY_BUCKET_NAME"]
    with pytest.raises(s3.exceptions.NoSuchKey):
        s3.get_object(Bucket=bucket, Key="public.pgp")
