from django.contrib.auth.models import User


class AuthHandler:
    NO_USER_MESSAGE = 'User does not exist!'
    WRONG_PWD_MESSAGE = 'Wrong password!'
    PWD_MUST_BE_SAME = 'Passwords does not match!'
    PWD_TOO_SHORT = 'Passwords must contain at least 8 characters!'
    
    
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
    
    def validate_same_password(self, password: str, confirm_password: str) -> str:
        is_valid = password == confirm_password
        if not is_valid: self.error_messages.append(self.PWD_MUST_BE_SAME)
        return is_valid
    
    def validate_password_len(self, password: str) -> bool:
        is_valid = password.__len__() >= 8
        if not is_valid: self.error_messages.append(self.PWD_TOO_SHORT)
        return is_valid
    
    def validate_password(self, password: str, confirm_password: str) -> bool:
        a,b = self.validate_password_len(password), self.validate_same_password(password, confirm_password) 
        return a and b       
        
        
        