from django.utils.functional import SimpleLazyObject
from rest_framework_simplejwt.authentication import JWTAuthentication
from myproject.utils import mark_user_online  # Import your tracking function
from rest_framework.exceptions import AuthenticationFailed
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import logging
from django.contrib.auth.models import AnonymousUser

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
            # If the user is already authenticated (e.g., via sessions), return them
            if request.user.is_authenticated:
                return request.user

           
            return AnonymousUser()

        except AuthenticationFailed as e:
            logger.error(f"Exception in _get_user: {e}")
            return AnonymousUser()

        except Exception as e:
            logger.error(f"Unexpected error in _get_user: {e}")
            return AnonymousUser()
        


from django.http import HttpResponseForbidden
#NOT INVOLVED NOW, CAN BE DELETED
from decouple import config
HOST_ADDRESS = config('HOST_ADDRESS','http://localhost:3001')
class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            print('REQUEST.user', request.user)
            if request.path in [f'{HOST_ADDRESS}/about']:  # Restricted page
                return HttpResponseForbidden("Upgrade to premium to access this page.")
        return self.get_response(request)