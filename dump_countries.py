import json
from django_setup import *
from profiles.models import Country


def main():
    countries = json.dumps([c.name for c in Country.objects.all()], indent=4)
    file = open('countries.json', 'w', encoding='utf-8')
    file.write(countries); file.close()


if __name__ == '__main__':
    main()
