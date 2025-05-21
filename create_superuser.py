from django_setup import *
from profiles.engine import UserHandler

def main():
    UserHandler(**dict(
        name = input('Name: '),
        email = input('Email: '),
        password = input('Password: '),
        is_superuser = True
    )).setup_user()


if __name__ == '__main__':
    main()