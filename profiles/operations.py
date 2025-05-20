from . import models


def create_unique_username_from_fullname(full_name: str, delimiter:str='_') -> str:
    tail = 0; 
    merge_username = lambda: f'{base_username}.{tail}'
    base_username = delimiter.join(full_name.split()).lower()
    username = merge_username()
    while models.User.objects.filter(username=username).exists():
        tail += 1; username = merge_username()
    return username
    
    
    