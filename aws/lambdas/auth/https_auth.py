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
    logging.warning(request)
    headers = request["headers"]
    custom_headers = request["origin"]["s3"]["customHeaders"]
    bucket = custom_headers["x-aws-distribution-bucket-name"][0]["value"]
    object = request["uri"].lstrip("/")
    id = ""
    secret = ""
    try:
        encoded_auth = headers["authorization"][0]["value"].lstrip("Basic ")
        decoded_auth = base64.b64decode(encoded_auth).decode("utf-8")
        id, secret = decoded_auth.split(":")
    except KeyError:
        pass
    try:
        session = boto3.Session(aws_access_key_id=id, aws_secret_access_key=secret)
        session.client("s3").get_object(Bucket=bucket, Key=object)
    except ClientError as e:
        logging.error(e)
        raise e
    return request
