import json
import os
import boto3
from auth_middleware import require_jwt

_secrets_cache = {}
secrets_client = boto3.client("secretsmanager")


@require_jwt
def lambda_handler(event, context):
    payload = event["jwt_payload"]
    user_id = event.get("pathParameters", {}).get("id")
    return {
        "statusCode": 200,
        "body": json.dumps({"user_id": user_id, "subject": payload.get("sub")})
    }
