from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models
from django.template.defaultfilters import slugify

from PIL import Image


class ItemFolder(models.Model):
    """
    Represents a folder for items, where you can add items related to each other, like color, flavor, size.

    This model handles function for manipulate with items.
    It's related to BaseItem as items' model for store all similarity items,
    and also having related to BaseItem as flavors for making a link between item and his flavor.
    """
    owner = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, db_index=True, related_name='folders')
    name = models.CharField(max_length=255, db_index=True, unique=True)
    slug = models.SlugField(max_length=255, editable=False, unique=True, db_index=True)
    flavors = models.ManyToManyField(to='BaseItem', related_name='folder')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail_folder', kwargs={'folder_slug': self.slug})

    def get_items_no_size(self):
        all_items = self.items.all().distinct(
            'name')  # Taking unique items by name (item having sizes with the same name).
        return all_items

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ItemWithSingleSize(models.Manager):
    def get_queryset(self):
        return BaseItem.objects.all().distinct('price', 'name')


class BaseItem(models.Model):
    """
    Represent an item model, to store the information about item.

    This models having function to get sizes of items or flavors.
    This model related to itemFolder model as items (To store items as single item with different sizes and flavors).
    Also, related to self for saving the sizes of item.
    """
    owner = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, db_index=True, related_name='items')
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=7)
    item_folder = models.ForeignKey('ItemFolder', on_delete=models.CASCADE, related_name='items')

    sizes = models.ManyToManyField('BaseItem', related_name='parent_item')

    size = models.CharField(max_length=255)

    flavor = models.CharField(max_length=255)

    direction = models.TextField(null=True, blank=True)
    ingredients = models.TextField(blank=True, null=True)

    type_of_food = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='items')

    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, related_name='items', db_index=True)

    objects = models.Manager()

    single_item = ItemWithSingleSize()  # manager to take the item without its size

    def get_sizes(self):
        """
        The function is returning all sizes linked with item
        """
        return self.sizes.all()

    def get_flavors(self):
        """
        The function is getting the flavors for item from the folder.
        """
        if self.folder.first():
            return self.folder.first().get_items_no_size()
        return None

    def __str__(self):
        return '#' + str(self.pk)

    def get_absolute_url(self):
        return reverse('detail_item', kwargs={'folder_slug': self.item_folder.slug, 'pk': self.pk})


class ImagesForBaseItem(models.Model):
    """
    Represent an images' model for saving images item.

    This model is saving images and resize them.
    The model is related to item as images.
    """
    base_item = models.ForeignKey('BaseItem', on_delete=models.CASCADE, related_name='images')
    image_of_item = models.ImageField(upload_to='items/%Y/%m/%d/')
    thumbnail_image = models.ImageField(upload_to='items/thumbnails/%Y/%m/%d/', editable=False, null=True, blank=True)

    def __str__(self):
        return self.base_item.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image = Image.open(self.image_of_item.path)
        resize = (350, 350)
        image.resize(resize, Image.LANCZOS)
        image.save(self.image_of_item.path, quality=100)


class Category(models.Model):
    """
    Represent a category model for searchin items by category.

    The model is related to item as type_of_food.
    """
    name = models.CharField(max_length=255, db_index=True, unique=True)
    slug = models.SlugField(max_length=255, db_index=True, unique=True, editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Animal(models.Model):
    """
    Represent an animal model for searching item by animal.

    The model can be reached using slug.
    The Model is rated to item as animal.
    """
    name = models.CharField(max_length=255, db_index=True, unique=True)
    slug = models.SlugField(max_length=255, editable=False, db_index=True, unique=True)
    image = models.ImageField(upload_to='animals/')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        image = Image.open(self.image.path)

        if image.width > 300 or image.height > 300:
            resize = (300, 300)
            image.thumbnail(resize)
            image.save(self.image.path)
