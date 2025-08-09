import json
import os
import boto3
import jwt
from jwt import InvalidTokenError

_secrets_cache = {}
secrets_client = boto3.client("secretsmanager")


def get_jwt_secret(secret_arn):
    if secret_arn in _secrets_cache:
        return _secrets_cache[secret_arn]
    env_secret = os.getenv("JWT_SECRET")
    if env_secret:
        _secrets_cache[secret_arn] = env_secret
        return env_secret
    resp = secrets_client.get_secret_value(SecretId=secret_arn)
    secret = resp.get("SecretString") or ""
    _secrets_cache[secret_arn] = secret
    return secret


def verify_jwt(token):
    secret_arn = os.environ.get("JWT_SECRET_ARN")
    secret = get_jwt_secret(secret_arn)
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except InvalidTokenError:
        return None


def lambda_handler(event, context):
    # Authorizationヘッダ: "Bearer <token>"
    auth = event.get("headers", {}).get("Authorization", "")
    if not auth.startswith("Bearer "):
        return {"statusCode": 401, "body": json.dumps({"message": "missing token"})}
    token = auth.split(" ", 1)[1]
    payload = verify_jwt(token)
    if not payload:
        return {"statusCode": 401, "body": json.dumps({"message": "invalid token"})}
    # 認可チェック (roles など) をここで行う
    user_id = event.get("pathParameters", {}).get("id")
    return {
        "statusCode": 200,
        "body": json.dumps({"user_id": user_id, "subject": payload.get("sub")})
    }
