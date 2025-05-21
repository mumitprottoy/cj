import cities_clean as cities
from django_setup import *
from profiles import models
from tqdm import tqdm 


def main():
    created = already_created = 0
    total = len(cities.cities)

    for city_data in tqdm(cities.cities, desc="Importing cities", unit="city", leave=False):
        country, _ = models.Country.objects.get_or_create(name=city_data['country'])
        if models.City.objects.filter(name=city_data['city'], country=country).exists():
            already_created += 1 
        else: 
            models.City.objects.create(name=city_data['city'], country=country)
            created += 1
    print(f'\nCreated: {created} / {total}')
    print(f'Already existed: {already_created} / {total}')
    print(f'Not Created: {total - already_created + created} / {total}')


if __name__ == '__main__':
    main()
