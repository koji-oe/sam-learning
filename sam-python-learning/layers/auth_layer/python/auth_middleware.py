import json
import os
import jwt
from jwt import InvalidTokenError


class AuthMiddleware:
    def __init__(self):
        self.jwt_secret = os.environ.get('JWT_SECRET')
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET is not set in environment variables")

    def verify_event(self, event):
        """
        ALB経由のeventからJWTを検証
        検証OKならpayloadを返し、NGなら401レスポンスを返す
        """
        headers = event.get('headers', {})
        auth = headers.get('Authorization')
        if not auth.startswith('Bearer '):
            return self._unauthorized("missing token")

        token = auth.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except InvalidTokenError:
            return self._unauthorized("invalid token")

    def _unauthorized(self, message):
        raise UnauthorizedException(message)


class UnauthorizedException(Exception):
    """
    認証失敗用例外
    """


def require_jwt(handler):
    def wrapper(event, context):
        auth = AuthMiddleware()
        try:
            payload = auth.verify_event(event)
        except UnauthorizedException as e:
            return {
                'statusCode': 401,
                'body': json.dumps({'message': str(e)})
            }

        # payloadをeventに追加して渡す
        event["jwt_payload"] = payload
        return handler(event, context)
    return wrapper
