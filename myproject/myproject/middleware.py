from django.utils.functional import SimpleLazyObject
from rest_framework_simplejwt.authentication import JWTAuthentication
from myproject.utils import mark_user_online  # Import your tracking function
from rest_framework.exceptions import AuthenticationFailed
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import logging

logger = logging.getLogger(__name__)

class OnlineUserTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request):
        # logger.info("OnlineUserTrackingMiddleware called")

        # Retrieve the user and mark them online
        user = self._get_user(request)
        if user.is_authenticated:  # Ensure it's a logged-in user
            mark_user_online(user.id)
            # logger.info(f"Marked user {user.username} (ID: {user.id}) as online.")

        # Keep the user lazy for later use
        request.user = SimpleLazyObject(lambda: user)
        return self.get_response(request)


#still have this error in console:backend-1            | 2025-02-10 02:13:40,121 ERROR    Exception in _get_user: {'detail': ErrorDetail(string='Token contained no recognizable user identification', code='token_not_valid'), 'code': ErrorDetail(string='token_not_valid', code='token_not_valid')}
    def _get_user(self, request):
        try:
            header = self.jwt_authenticator.get_header(request)
            if header is None:
                logger.info("No Authorization header found.")
                return request.user  # Return AnonymousUser

            raw_token = self.jwt_authenticator.get_raw_token(header)
            validated_token = self.jwt_authenticator.get_validated_token(raw_token)
            # Ensure token is valid
            if validated_token:
                user = self.jwt_authenticator.get_user(validated_token)
                # logger.info(f"Authenticated user: {user.username} (ID: {user.id})")
                return user
            else:
                logger.info("Token is not valid.")
            return request.user
        except (AuthenticationFailed, jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError) as e:
            logger.error(f"Exception in _get_user: {e}")
            return request.user