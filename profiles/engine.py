import re
from . import models


"""
Handles User Creation
"""
class UserHandler:
    NAME_REGEX = r"^[A-Za-z]+(?: [A-Za-z]+)+$"
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    NAME_MESSAGE = 'Name should have at least two parts, can only contain and start with alphabets (A-Z & a-z) separated by spaces.'
    DUPLICATE_EMAIL_MESSAGE = 'Email already exists.'
    INVALID_EMAIL_MESSAGE = 'Invalid email syntax.'
    PASSWORD_MESSAGE = 'Password must contain at least 8 charcaters.'

    def __init__(self, name: str, email: str, password: str, is_superuser: bool=False) -> None:
        self.name = name
        self.email = email
        self.password = password
        self.is_superuser = is_superuser
        self.error_messages = list()
    
    def clean_name(self) -> str:
        name = ' '.join([part.strip() for part in self.name.split()])
        name = name.lower().title()
        self.name = name
        return self.name
    
    def get_names(self) -> tuple[str, str]:
        return self.name.split()[0], ' '.join(self.name.split()[1:])
    
    def validate_name(self) -> bool: 
        is_valid = re.match(self.NAME_REGEX, self.name)
        if not is_valid: self.error_messages.append(self.NAME_MESSAGE)
        return is_valid
        
    def validate_email(self) -> bool:
        is_unique = not models.User.objects.filter(email=self.email).exists()
        is_valid = re.match(self.EMAIL_REGEX, self.email)
        if not is_unique: self.error_messages.append(self.DUPLICATE_EMAIL_MESSAGE)
        if not is_valid: self.error_messages.append(self.INVALID_EMAIL_MESSAGE)
        return is_unique and is_valid
    
    def validate_password(self) -> bool:
        is_valid = self.password.__len__() >= 8
        if not is_valid: self.error_messages.append(self.PASSWORD_MESSAGE)
        return is_valid
    
    def validate_data(self) -> bool:
        x,y,z = self.validate_name(), self.validate_email(), self.validate_password()
        return x and y and z
    
    @property
    def errors(self) -> list:
        return list(set(self.error_messages))
    
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
                is_staff=self.is_superuser
            )
    
    def setup_user(self) -> models.User:
        if self.validate_data():
            data = self.prepare_data()
            if not models.User.objects.filter(**data).exists():
                user = models.User(**data); user.save()
                user.set_password(self.password); user.save()
                print('Created user.')
                print(user.__dict__)
                # user.codes.send_verification_code()
                return user, dict(user_id=user.id)
            print('User already exists.')
        else: print('errors:', self.error_messages)
        
        
        
"""
Handles User profile Deliveries, Creations and Updates
"""
class ProfileEngine:
    POP_KEY = '_state'
    
    def __init__(self, user: models.User) -> None:
        self.user = user      
    
    @property
    def primary(self) -> dict:
        return dict(
            id=self.user.id,
            name=self.user.get_full_name(),
            nickname=self.user.nickname.name,
            email=self.user.email
        )
    
    @property
    def birthdate(self) -> dict:
        return dict(
            user_id=self.user.id,
            date=self.user.birth_date.date
        )
    
    @property
    def pics(self) -> dict:
        return dict(
            user_id=self.user.id,
            profile_pic_url=self.user.pics.profile_pic_url,
            cover_pic_url=self.user.pics.cover_pic_url,
        )
    
    @property
    def address(self) -> dict:
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
    def has_addr_data(self) -> bool:
        addr = self.address
        values = [bool(v) for v in list(addr.values())]
        return sum(values) == values.__len__()
    
    @property
    def details(self) -> dict:
        return dict(
            id=self.user.id,
            primary=self.primary,
            pics=self.pics,
            birth_date=self.birthdate,
            address=self.address
        )
    
    def update_primary(self, **kwargs) -> dict:
        pass
    
    def pretty_print(self) -> None:
        import json
        print(json.dumps(self.detailed_profile, indent=4))
