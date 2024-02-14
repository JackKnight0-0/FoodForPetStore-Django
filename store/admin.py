from django.contrib import admin
from .models import Category, Animal, BaseItem, ImagesForBaseItem, ItemFolder


@admin.register(ItemFolder)
class ItemFolderAdmin(admin.ModelAdmin):
    readonly_fields = ['slug', ]


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    exclude = ['slug', ]


@admin.register(BaseItem)
class BaseItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'price']
    exclude = ['slug', ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]


@admin.register(ImagesForBaseItem)
class ImagesForBaseItemAdmin(admin.ModelAdmin):
    pass
