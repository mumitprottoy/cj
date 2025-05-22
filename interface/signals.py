import random
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from profiles import models as profile_models, engine


# @receiver(pre_save, sender=User)
# def add_unique_username(instance: User, *args, **kwargs) -> None:
#     user = instance
#     user.username = engine.UserHandler.create_unique_username(
#         f"{user.first_name} {user.last_name}")


@receiver(post_save, sender=User)
def add_birdth_date(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.BirthDate.objects.create(user=user)


@receiver(post_save, sender=User)
def add_address(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.Address.objects.create(user=user)


@receiver(post_save, sender=User)
def add_auth_code(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.AuthCode.objects.create(user=user)


@receiver(post_save, sender=User)
def add_nickname(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.Nickname.objects.create(user=user)


@receiver(post_save, sender=User)
def add_pics(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        pic_id = str(random.randint(1,50))
        pp_url = f'https://i.pravatar.cc/150?img={pic_id}'
        cp_url = f'https://picsum.photos/id/{pic_id}/800/300'
        profile_models.Pic.objects.create(
            user=user,
            profile_pic_url=pp_url,
            cover_pic_url=cp_url,
        )

