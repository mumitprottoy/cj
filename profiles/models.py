from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone as tz
from utils import constants as const, keygen


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = 'Countries'
    
    def __str__(self) -> str:
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    
    class Meta:
        verbose_name_plural = 'Cities'
    
    
    def __str__(self) -> str:
        return f'{self.name}, {self.country.name}'

    @property
    def display_name(self) -> str:
        return self.__str__() 


class Pic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pics')
    profile_pic_url = models.TextField(default='')
    cover_pic_url = models.TextField(default='')
    
    def __str__(self) -> str:
        return self.user.email 


class BirthDate(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='birth_date')
    date = models.DateField(null=True, blank=True, default=None)
    
    @property
    def date_str(self) -> str | None:
        if self.date is None: return ''
        return self.date.strftime(const.DATE_STR_FORMAT_1)
        
    def __str__(self) -> str:
        return f'{self.user.email} | {self.user.username} | {self.date_str}'


class Address(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='address', null=True, blank=True, default=None)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True, default=None)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, null=True, blank=True, default=None)
    post_code = models.CharField(max_length=15, null=True, blank=True, default='')
    details = models.TextField(null=True, blank=True, default='')
    
    class Meta:
        verbose_name_plural = 'User Address'
    
    def __str__(self) -> str:
        return self.user.email + ' | ' + self.user.username
    

class AuthCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='codes')
    otp = models.CharField(max_length=4, default='') 
    verification_code = models.CharField(max_length=4, default='')
    is_email_verified = models.BooleanField(default=False)
    
    def __generate_code(self):
        kg = keygen.KeyGen()
        return kg.num_key(key_len=4)
    
    def change_otp(self):
        self.otp = self.__generate_code()
        self.save()
    
    def change_verification_code(self):
        self.verification_code = self.__generate_code()
        self.save()
    
    # def send_otp(self):
    #     self.change_otp()
    #     self.send_code('OTP')
    
    # def send_verification_code(self):
    #     self.change_verification_code()
    #     self.send_code('verification code')
        
    def verify_email(self):
        self.is_email_verified = True
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = self.__generate_code()
        if not self.verification_code:
            self.verification_code = self.__generate_code()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.user.email
