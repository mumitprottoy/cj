from django_setup import *
from new_countries import countries
from profiles import models
from tqdm import tqdm


if input('Clear Country and City Tables? (yes/no): ').lower() == 'yes':
    print('Clearing Country and City Tables...')
    models.Country.objects.all().delete()
    print('Cleared.')


print('\nPreparing new countries and cities...')
for data in tqdm(countries, desc='Adding countries... ', unit=' country', leave=True):
    country, created = models.Country.objects.create(name=data['name'])
    if created:
        for city in tqdm(
            data['cities'], desc=f'Adding cities to {data["name"]}', unit=' city', leave=True):
            city = models.City(country=country, name=city['name'])
            city.save()

print('\nTotal countries:', models.Country.objects.count())
print('Total cities:', models.City.objects.count())

