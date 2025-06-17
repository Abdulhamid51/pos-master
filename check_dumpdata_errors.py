import django
import os
import subprocess
from django.apps import apps

# Django muhitini sozlash
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domstroy.settings")
django.setup()

# Har bir model bo‘yicha tekshirish
for model in apps.get_models():
    app_label = model._meta.app_label
    model_name = model.__name__
    full_name = f"{app_label}.{model_name}"
    print(f"Testing: {full_name}")
    try:
        subprocess.run(
            ["python3", "manage.py", "dumpdata", full_name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print(f"❌ ERROR in model: {full_name}")
