import unicodedata
import json
from tqdm import tqdm
from cities import cities


def clean_text(s):
    # Normalize accents
    nfkd_form = unicodedata.normalize('NFKD', s)
    no_accents = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Remove any kind of quotation marks by replacing with empty string
    quotes = ["'", '"', '’', '‘', '“', '”']
    for q in quotes:
        no_accents = no_accents.replace(q, "")
    
    return no_accents


def main():
    cleaned_cities = []
    
    for city_data in tqdm(cities):
        cleaned_country = clean_text(city_data['country'])
        cleaned_city = clean_text(city_data['city'])
        cleaned_cities.append({'country': cleaned_country, 'city': cleaned_city})
    
    # Write cleaned data to cities.py file as JSON list assigned to 'cities'
    with open('cities_clean.py', 'w', encoding='utf-8') as f:
        f.write("cities = ")
        json.dump(cleaned_cities, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
