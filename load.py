import subprocess

print('\nInstalling necessary packages with pip...')
subprocess.run('pip install -r requirements.txt', shell=True)

from django_setup import *

if input('Stage Migration? (yes/no): ').lower() == 'yes':
    subprocess.run('python manage.py makemigrations', shell=True)
    if input('Migrate? (yes/no): ').lower() == 'yes':
        subprocess.run('python manage.py migrate', shell=True)


if input('\nFlush DB first? (yes/no): ').lower() == 'yes':
    print('Flushing DB...')
    subprocess.run('python manage.py flush', shell=True)
    print('DB flushed.')

print('\nChecking data.json file integrity...')

import json
from django_setup import *
from django.apps import apps
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType


from django.contrib.auth.models import Permission, User  # Adjust as needed

with open("data.json") as f:
    data = json.load(f)

def resolve_foreign_keys(fields):
    # Resolve FK IDs (basic resolution)
    for key, value in fields.items():
        if key.endswith("_id") or key in ["user", "content_type"]:
            try:
                fields[key] = int(value)
            except:
                pass
    return fields

def get_lookup_fields(model_label, fields, pk):
    """
    Determine unique constraints for update_or_create
    """
    if model_label == "contenttypes.contenttype":
        return {
            "app_label": fields["app_label"],
            "model": fields["model"]
        }

    elif model_label == "auth.permission":
        return {
            "content_type_id": fields["content_type"],
            "codename": fields["codename"]
        }

    elif model_label == "auth.user":
        return {
            "username": fields["username"]
        }

    # Fallback: use primary key
    return {"pk": pk}

def safely_set_m2m(obj, fields):
    """
    Apply many-to-many fields after save
    """
    for field_name, value in fields.items():
        if isinstance(value, list):
            try:
                getattr(obj, field_name).set(value)
            except Exception:
                continue

def process_record(record):
    model_label = record["model"]
    pk = record["pk"]
    fields = record["fields"]
    fields = resolve_foreign_keys(fields)

    Model = apps.get_model(model_label)

    lookup = get_lookup_fields(model_label, fields, pk)

    if "pk" not in lookup:
        fields["id"] = pk

    m2m_fields = {k: fields.pop(k) for k in list(fields) if isinstance(fields[k], list)}

    try:
        obj, created = Model.objects.update_or_create(
            **lookup,
            defaults=fields
        )
        safely_set_m2m(obj, m2m_fields)
        print(f"{'✅ Created' if created else '🔁 Updated'}: {model_label} (pk={pk})")

    except IntegrityError as e:
        print(f"⚠️ Skipped {model_label} (pk={pk}) due to IntegrityError: {e}")
    except Exception as e:
        print(f"❌ Error processing {model_label} (pk={pk}): {e}")

# 🚀 Run the import loop
for record in data:
    process_record(record)

print('Loading db data...')
subprocess.run('python manage.py loaddata data.json', shell=True)
print('\n✅ Loading completed.')
