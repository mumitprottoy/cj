import re
from . import models


class UserHandler:
    REGEX = "^[A-Za-z]+(?: [A-Za-z]+)+$"
    NAME_MESSAGE = 'Name should only contain and start with alphabets (A-Z & a-z) separated by spaces.'
    EMAIL_MESSAGE = 'Email already exists.'
    PASSWORD_MESSAGE = 'Password must contain at least 8 charcaters.'

    def __init__(self, name: str, email: str, password: str, is_superuser: bool=False) -> None:
        self.name = name
        self.email = email
        self.password = password
        self.is_superuser = is_superuser
        self.error_messages = dict()
    
    def clean_name(self) -> str:
        name = ' '.join([part.strip() for part in self.name.split()])
        name = name.lower().title()
        self.name = name
        return self.name
    
    def get_names(self) -> tuple[str, str]:
        return self.name.split()[0], ' '.join(self.name.split()[1:])
    
    def validate_name(self) -> bool: 
        valid = re.match(self.REGEX, self.name)
        if not valid: self.error_messages['Name'] = self.NAME_MESSAGE
        return valid
        
    def validate_email(self) -> bool:
        valid = not models.User.objects.filter(email=self.email).exists()
        if not valid: self.error_messages['Email'] = self.EMAIL_MESSAGE
        return valid
    
    def validate_password(self) -> bool:
        valid = self.password.__len__() >= 8
        if not valid: self.error_messages['Password'] = self.PASSWORD_MESSAGE
        return valid
    
    def validate_data(self) -> bool:
        return self.validate_name() and self.validate_email() and self.validate_password()
    
    @classmethod
    def create_unique_username(cls, full_name: str, delimiter: str='.') -> str: 
        tail = 0
        merge_username = lambda base_username, tail: f'{base_username}.{tail}'
        base_username = delimiter.join(full_name.split()).lower()[:10]
        username = merge_username(base_username, tail)
        print(username, models.User.objects.filter(username=username).exists())
        while models.User.objects.filter(username=username).exists():
            tail += 1; username = merge_username(base_username, tail)
            print(username)
        return username
        
    def prepare_data(self) -> dict:
        validated = self.validate_data()
        if validated:
            self.clean_name()
            first_name, last_name = self.get_names()
            return dict(
                first_name=first_name,
                last_name=last_name,
                username=self.create_unique_username(f'{first_name} {last_name}'),
                email=self.email,
                is_superuser=self.is_superuser,
                is_staff=self.is_superuser,
            )
    
    def setup_user(self) -> models.User:
        if self.validate_data():
            data = self.prepare_data()
            if not models.User.objects.filter(**data).exists():
                user = models.User(**data); user.save()
                user.set_password(self.password); user.save()
                print('Created user.')
                print(user.__dict__)
                return user
            print('User already exists.')
        else: print('errors:', self.error_messages)
        

class ProfileEngine:
    POP_KEY = '_state'
    
    def __init__(self, user: models.User) -> None:
        self.user = user      
    
    @property
    def primary_data(self) -> dict:
        return dict(
            id=self.user.id,
            name=self.user.get_full_name(),
            email=self.user.email
        )
    
    @property
    def birth_date_data(self) -> dict:
        return dict(
            user_id=self.user.id,
            date=self.user.birth_date.date
        )
    
    @property
    def pics_data(self) -> dict:
        return dict(
            user_id=self.user.id,
            profile_pic_url=self.user.pics.profile_pic_url,
            cover_pic_url=self.user.pics.cover_pic_url,
        )
    
    @property
    def address_data(self) -> dict:
        country = city = str()
        if self.user.address.city is not None:
            city = self.user.address.city.name
            country = self.user.address.city.country.name
        return dict(
            user_id=self.user.id,
            country=country,
            city=city,
            post_code=self.user.address.post_code,
            details=self.user.address.details,
        )
    
    @property
    def detailed_profile(self) -> dict:
        return dict(
            id=self.user.id,
            primary=self.primary_data,
            pics=self.pics_data,
            birth_date=self.birth_date_data,
            address=self.address_data
        )
    
    def pretty_print(self) -> None:
        import json
        print(json.dumps(self.detailed_profile, indent=4))
