import json
import os
import boto3
import jwt
from datetime import datetime, timedelta

_secrets_cache = {}
secrets_client = boto3.client('secretsmanager')


def get_jwt_secret(secret_arn):
    if secret_arn in _secrets_cache:
        return _secrets_cache[secret_arn]
    # ローカル開発向け: 環境変数 JWT_SECRET が設定されている場合はそれを使用
    env_secret = os.environ.get('JWT_SECRET')
    if env_secret:
        _secrets_cache[secret_arn] = env_secret
        return env_secret
    resp = secrets_client.get_secret_value(SecretId=secret_arn)
    secret = resp.get('SecretString') or ""
    _secrets_cache[secret_arn] = secret
    return secret


def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    username = body.get("username")
    password = body.get("password")
    # --- ここはサンプル: 実運用ではユーザ確認(DB)をする ---
    if username == "alice" and password == "password":
        secret_arn = os.environ.get("JWT_SECRET_ARN")
        secret = get_jwt_secret(secret_arn)
        payload = {
            "sub": username,
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + timedelta(minutes=60)).timestamp(),
            "roles": ["user"]
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return {
            "statusCode": 200,
            "body": json.dumps({"token": token})
        }
    else:
        return {"statusCode": 401, "body": json.dumps({"message": "invalid credentials"})}
