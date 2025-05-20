from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(pre_save, sender=User)
def add_unique_username(instance: User, created: bool, *args, **kwargs) -> None:
    pass