from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from profiles import operations as profile_ops


@receiver(pre_save, sender=User)
def add_unique_username(instance: User, *args, **kwargs) -> None:
    user = instance
    user.username = profile_ops.create_unique_username_from_fullname(
        f"{user.first_name} {user.last_name}")