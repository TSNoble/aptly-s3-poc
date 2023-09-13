import os
import base64
import logging

import boto3
from botocore.exceptions import ClientError


UNAUTHORIZED_RESPONSE = {
    "status": 401,
    "statusDescription": "Unauthorized",
}


def handler(event, _):
    request = event["Records"][0]["cf"]["request"]
    headers = request["headers"]
    logging.warning(headers)
    try:
        encoded_auth = headers["authorization"][0]["value"].lstrip("Basic ")
        decoded_auth = base64.b64decode(encoded_auth).decode("utf-8")
        id, secret = decoded_auth.split(":")
        session = boto3.Session(aws_access_key_id=id, aws_secret_access_key=secret)
        bucket = os.environ["AWS_DEPLOYMENT_BUCKET_NAME"]
        session.client("s3").get_object(Bucket=bucket, Key="index.html")
        return request
    except (KeyError, ClientError) as e:
        logging.error("Request does not contain expected authorization headers")
        return UNAUTHORIZED_RESPONSE
    except ClientError as e:
        logging.error(e.response["Error"])
        return UNAUTHORIZED_RESPONSE
