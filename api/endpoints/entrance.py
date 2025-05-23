from .libs import *
from profiles import models as profile_models, engine as profile_engine
from entrance import engine as auth_engine
from .. import lifetime, messages as msg, tokens


class RegisterAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        handler = profile_engine.UserHandler(**request.data)
        is_valid = handler.validate_data()
        if is_valid:
            user, _ = handler.setup_user()
            profile = profile_engine.ProfileEngine(user)
            return Response(profile.primary, status=status.HTTP_200_OK)
        return Response(dict(errors=handler.errors), status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        handler = auth_engine.AuthHandler()
        user = handler.authenticate_with_email(**request.data)
        if user is not None:
            token_handler = tokens.TokenHandler()
            token_data = token_handler.get_token_data_by_user(user)
            token_data['user_id'] = user.id
            profile = profile_engine.ProfileEngine(user)
            token_data['has_addr_data'] = profile.has_addr_data
            return Response(token_data, status=status.HTTP_200_OK)
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
            token_handler = tokens.TokenHandler()
            token_data = token_handler.get_token_data_by_refresh_token(refresh_token)
            token_data['user_id'] = request.user.id
            return Response(token_data, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response(dict(errors=[msg.INVALID_REFRESH_TOKEN]), status=status.HTTP_401_UNAUTHORIZED)
        

class EmailVerificationAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated: 
            if profile_models.AuthCode.verify_email_before_login(**request.data):
               return Response(dict(message=msg.EMAIL_VERIFIED), status=status.HTTP_200_OK)
            return Response(dict(errors=[msg.INVALID_CODE]), status=status.HTTP_401_UNAUTHORIZED) 
        return Response(dict(errors=[msg.ALREADY_LOGGED_IN]), status=status.HTTP_400_BAD_REQUEST)


class OTPRequestAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            if user is not None:
                if user.codes.send_otp():
                    return Response(dict(email=email, message=msg.OTP_SENT), status=status.HTTP_200_OK)
                return Response(dict(errors=[msg.OTP_SENDING_FAILED]), status=status.HTTP_400_BAD_REQUEST)
            return Response(dict(errors=[msg.UNKNOWN_ERROR]), status=status.HTTP_400_BAD_REQUEST)
        return Response(dict(errors=[msg.ALREADY_LOGGED_IN]), status=status.HTTP_400_BAD_REQUEST)
        

class OTPVerificationAPI(views.APIView):
    
    def post(self, request: Request) -> Response:
        if not request.user.is_authenticated: 
            if profile_models.AuthCode.verify_email_before_login(**request.data):
                user = User.objects.get(email=request.data.get('email'))
                profile = profile_engine.ProfileEngine(user)
                response = dict(user_id=user.id, message=msg.OTP_VERIFIED, has_addr_data=profile.has_addr_data)
                tokens_handler = tokens.TokenHandler()
                token_data = tokens_handler.get_token_data_by_user(user)
                response.update(token_data)
                return Response(response, status=status.HTTP_200_OK)
            return Response(dict(errors=[msg.INVALID_CODE]), status=status.HTTP_401_UNAUTHORIZED) 
        return Response(dict(errors=[msg.ALREADY_LOGGED_IN]), status=status.HTTP_400_BAD_REQUEST)


class PwdChangeAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request: Request) -> Response:
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        handler = auth_engine.AuthHandler()
        is_valid = handler.validate_password(password, confirm_password)
        if is_valid:
            request.user.set_password(password)
            request.user.save()
            return Response(dict(message=msg.PWD_CHANGE_SUCCESS), status=status.HTTP_200_OK)
        return Response(dict(errors=handler.errors), status=status.HTTP_400_BAD_REQUEST)
     