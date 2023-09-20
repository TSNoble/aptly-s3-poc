import os

import pytest
import boto3


def test_unauthenticated_user_cannot_access_public_key():
    session = boto3.Session(aws_access_key_id="foo", aws_secret_access_key="bar")
    s3 = session.client("s3")
    bucket = os.environ["AWS_APTLY_BUCKET_NAME"]
    try:
        s3.get_object(Bucket=bucket, Key="public.pgp")
        pytest.fail("Should not be able to access public key")
    except s3.exceptions.ClientError as e:
        print(e)
        assert e.error_code == "AccessDenied"
