import cities
from django_setup import *
from profiles import models


def main():
    created = already_created = 0
    total = cities.cities.__len__()
    
    for city_data in cities.cities:
        country = models.Country.objects.get_or_create(name=city_data['country'])
        if models.City.objects.filter(
            name=city_data['city'], country=country).exists():
            already_created += 1
        else:
            models.City.objects.create(name=city_data['city'], country=country)
            created += 1
    
    print(f'created: {created} / {total}')
    print(f'already created: {already_created} / {total}')


if __name__ == '__main__':
    main()
