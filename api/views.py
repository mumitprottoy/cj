from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import views, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from profiles import models as profile_models, engine as profile_engine
from entrance import engine as auth_engine
from . import lifetime, messages as msg


class RegisterAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        handler = profile_engine.UserHandler(**request.data)
        is_valid = handler.validate_data()
        if is_valid:
            user, _ = handler.setup_user()
            profile = profile_engine.ProfileEngine(user)
            return Response(profile.primary_data, status=status.HTTP_201_CREATED)
        return Response(dict(errors=handler.errors), status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        handler = auth_engine.AuthHandler()
        user = handler.authenticate_with_email(**request.data)
        if user is not None:
            token_bearer = RefreshToken.for_user(user)
            access_token = str(token_bearer.access_token)
            refresh_token = str(token_bearer)
            access_token_lifetime_remaining = lifetime.get_token_lifetime_remaining_days(access_token)
            refresh_token_lifetime_remaining = lifetime.get_token_lifetime_remaining_days(refresh_token)
            return Response(dict(
                user_id = user.id,
                access_token = access_token,
                refresh_token = refresh_token,
                access_token_lifetime_remaining = access_token_lifetime_remaining,
                refresh_token_lifetime_remaining = refresh_token_lifetime_remaining
            ), status=status.HTTP_200_OK)
        return Response(dict(errors=handler.errors), status=status.HTTP_401_UNAUTHORIZED)
    

class TokenLifetimeAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: Request) -> Response:
        return Response(
            lifetime.get_token_remaining_days_with_request(request), status=status.HTTP_200_OK)    
            
        
class RefreshTokenAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response(dict(errors=[msg.REFRESH_TOKEN_NOT_PROVIDED]), status=status.HTTP_400_BAD_REQUEST)

        try:
            token_bearer = RefreshToken(refresh_token)
            access_token = str(token_bearer.access_token)
            refresh_token = str(token_bearer)
            access_token_lifetime_remaining = lifetime.get_token_lifetime_remaining_days(access_token)
            refresh_token_lifetime_remaining = lifetime.get_token_lifetime_remaining_days(refresh_token)
            return Response(dict(
                user_id = request.user.id,
                access_token = access_token,
                refresh_token = refresh_token,
                access_token_lifetime_remaining = access_token_lifetime_remaining,
                refresh_token_lifetime_remaining = refresh_token_lifetime_remaining
            ), status=status.HTTP_200_OK)
        except TokenError as e:
            return Response(dict(errors=[msg.INVALID_REFRESH_TOKEN]), status=status.HTTP_401_UNAUTHORIZED)
        

class ProfileAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request, data_type: str) -> Response:
        user = request.user
        profile = profile_engine.ProfileEngine(user)
        return Response(
            profile_engine.ProfileEngine.__dict__[data_type].fget(profile), status=status.HTTP_200_OK)
    
            
