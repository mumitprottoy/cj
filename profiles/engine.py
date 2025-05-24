import re, json, datetime
from . import models, constants as const, messages as msg


"""
Handles User Creation
"""
class UserHandler:

    def __init__(self, name: str, email: str, password: str, is_superuser: bool=False) -> None:
        self.name = name
        self.email = email
        self.password = password
        self.is_superuser = is_superuser
        self.error_messages = list()
    
    @classmethod
    def clean_name(self, name=None) -> str:
        if name is None: name = self.name
        name = ' '.join([part.strip() for part in name.split()])
        name = name.lower().title()
        return name
    
    @classmethod
    def get_names(self, name=None) -> tuple[str, str]:
        if name is None: name = self.name
        name = self.clean_name(name) 
        return name.split()[0], ' '.join(name.split()[1:])
    
    @classmethod
    def validate_name(self, name=None) -> bool:
        if name is None: name = self.name 
        is_valid = re.match(const.NAME_REGEX, name)
        try:
            if not is_valid: self.error_messages.append(msg.INVALID_NAME)
        except: pass
        return is_valid
    
    @classmethod
    def validate_nickname(self, nickname=str) -> bool: 
        is_valid = re.match(const.NICKNAME_REGEX, nickname)
        try:
            if not is_valid: self.error_messages.append(msg.INVALID_NICKNAME)
        except: pass
        return is_valid
        
    def validate_email(self) -> bool:
        is_unique = not models.User.objects.filter(email=self.email).exists()
        is_valid = re.match(const.EMAIL_REGEX, self.email)
        try:
            if not is_unique: self.error_messages.append(msg.DUPLICATE_EMAIL_MESSAGE)
            if not is_valid: self.error_messages.append(msg.INVALID_EMAIL_MESSAGE)
        except: pass
        return is_unique and is_valid
    
    def validate_password(self) -> bool:
        is_valid = self.password.__len__() >= 8
        try:
            if not is_valid: self.error_messages.append(msg.PASSWORD_MESSAGE)
        except: pass
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
        is_validated = self.validate_data()
        if is_validated:
            data = self.prepare_data()
            if not models.User.objects.filter(**data).exists():
                user = models.User(**data); user.save()
                user.set_password(self.password); user.save()
                print('Created user.')
                print(user.__dict__)
                # user.codes.send_verification_code()
                return user
            print('User already exists.')
        else: print('errors:', self.error_messages)
        
        
        
"""
Handles User profile Deliveries, Creations and Updates
"""
class ProfileEngine:
    
    def __init__(self, user: models.User) -> None:
        self.user = user
        self.error_messages = list()      
    
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
            date=self.user.birth_date.timestamp_ms
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
            has_addr_data=self.has_addr_data,
            primary=self.primary,
            pics=self.pics,
            birth_date=self.birthdate,
            address=self.address
        )
        
    @property
    def errors(self) -> list:
        return list(set(self.error_messages))
    
    def validate_country(self, country_name: str) -> bool:
        is_valid = models.Country.objects.filter(name=country_name).exists()
        if not is_valid: self.error_messages.append(msg.NO_COUNTRY)
        return is_valid
    
    def validate_city(self, country_name: str, city_name: str) -> bool:
        is_valid = models.City.objects.filter(country__name=country_name, name=city_name).exists()
        if not is_valid: self.error_messages.append(msg.NO_CITY)
        return is_valid
        
    def validate_country_and_city(self, country_name: str, city_name: str) -> bool:
        a,b = self.validate_country(country_name), self.validate_city(country_name, city_name)
        return a and b
    
    def validate_name(self, name: str) -> bool:
        is_valid = UserHandler.validate_name(name)
        if not is_valid: self.error_messages.append(msg.INVALID_NAME)
        return is_valid
    
    def validate_nickname(self, nickname: str) -> bool:
        is_valid = UserHandler.validate_nickname(nickname)
        if not is_valid: self.error_messages.append(msg.INVALID_NICKNAME)
        return is_valid
    
    def validate_primary(self, name: str, nickname: str) -> bool:
        a, b = self.validate_name(name), self.validate_nickname(nickname)
        return a and b
    
    def update_name(self, name: str) -> None:
        self.user.first_name, self.user.last_name = UserHandler.get_names(name)
        self.user.save()
    
    def update_nickname(self, nickname: str) -> None:
        self.user.nickname.name = nickname
        self.user.nickname.save()
    
    def update_primary(self, name: str, nickname: str, date: int) -> dict | None:
        if self.validate_primary(name, nickname):
            self.update_name(name)
            self.update_nickname(nickname)
            self.update_birthdate
            return self.primary
    
    def update_birthdate(self, date: int):
        birthdate = datetime.datetime.fromtimestamp(int(date)/1000).date()
        self.user.birth_date.date = birthdate
        self.user.birth_date.save()
        return self.birthdate
    
    def update_address(
        self, country: str, city: str, post_code: str, details: str) -> dict | None:
        if self.validate_country_and_city(country, city):
            city = models.City.objects.get(country__name=country, name=city)
            self.user.address.city = city
            self.user.address.post_code = post_code
            self.user.address.details = details
            self.user.address.save()
            return self.address
    
    def pretty_print(self) -> None:
        print(json.dumps(self.detailed_profile, indent=4))
