import json

from django.db import transaction

from recipes.models import Ingredient

with open('ingredients.json', encoding='utf-8') as f:
    data = json.load(f)

    with transaction.atomic():
        for ingredient in data:
            Ingredient.objects.create(
                name=ingredient["name"],
                measurement_unit=ingredient["measurement_unit"])
