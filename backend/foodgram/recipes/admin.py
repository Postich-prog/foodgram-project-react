from django.contrib import admin

from .models import Ingredient, Recipe, Tag, User

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(User)
