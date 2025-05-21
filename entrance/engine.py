from django.contrib.auth.models import User


class AuthHandler:
    NO_USER_MESSAGE = 'User does not exist.'
    WRONG_PWD_MESSAGE = 'Wrong password.'
    
    def __init__(self) -> None:
        self.error_messages = list()
    
    def authenticate_user(self, key: str, value: str, password: str) -> User | None:
        user = User.objects.filter(**{key:value}).first()
        if user is not None:
            if user.check_password(password):
                return user
            self.error_messages.append(self.WRONG_PWD_MESSAGE)
        else: self.error_messages.append(self.NO_USER_MESSAGE)
    
    @property
    def errors(self) -> list:
        return list(set(self.error_messages))
    
    def authenticate_with_email(self, email:str, password: str) -> User | None:
        return self.authenticate_user('email', email, password)
    
    def authenticate_with_username(self, username: str, password: str) -> User | None:
        return self.authenticate_user('username', username, password)
        
        