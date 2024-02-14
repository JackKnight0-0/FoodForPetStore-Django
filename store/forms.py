from django import forms
from django.forms.models import BaseModelFormSet
from .models import BaseItem, ImagesForBaseItem, ItemFolder
from .models import BaseItem, ImagesForBaseItem, ItemFolder


class CreateItemFolderForm(forms.ModelForm):
    """
    Form for creating item folder
    """

    class Meta:
        model = ItemFolder
        fields = (
            'name',
        )

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of item folder'})
        }


class CreateBaseItemForm(forms.ModelForm):
    """
    Form for creating a base item.
    """
    size = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Size'}))

    class Meta:
        model = BaseItem
        fields = (
            'name',
            'description',
            'direction',
            'type_of_food',
            'quantity',
            'price',
            'flavor',
            'size',
            'ingredients',
            'animal',
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of product'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'direction': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Direction'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Price per item'}),
            'flavor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Flavor'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingredients'}),
            'animal': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Animal'}),
            'type_of_food': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Animal'})
        }

    def clean_name(self):
        """
        Custom clean method to check if the name of the base item already exists.
        """
        name = self.cleaned_data.get('name')
        if BaseItem.objects.filter(name__icontains=name).exists():
            self.add_error('name', 'This name already taken!')
        return name


class AddSizeFoodForm(forms.ModelForm):
    """
    Form for adding size to food.
    """

    class Meta:
        model = BaseItem
        fields = (
            'size',
            'description',
            'quantity',
            'price',
            'direction',
        )
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'direction': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Direction'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Price per item'}),
            'size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Size'}),
        }

    def __init__(self, *args, **kwargs):
        self.parent_item = kwargs.pop('parent_item', None)
        super(AddSizeFoodForm, self).__init__(*args, **kwargs)

    def clean_size(self):
        """
        Custom clean method to check if the size already exists for this item.
        """
        size = self.cleaned_data.get('size')
        if self.parent_item.sizes.filter(size=size).exists():
            self.add_error('size', 'This size already exists for this item')
        return size


class CreateImagesForItemForm(forms.ModelForm):
    """
    Form for creating images for a base item.
    """

    class Meta:
        model = ImagesForBaseItem
        fields = (
            'image_of_item',
        )


class ImageItemFormset(BaseModelFormSet):
    """
    Formset for handling images of base items.
    """

    def __init__(self, *args, **kwargs):
        super(ImageItemFormset, self).__init__(*args, **kwargs)
        self.queryset = ImagesForBaseItem.objects.none()


image_formset = forms.modelformset_factory(model=ImagesForBaseItem, form=CreateImagesForItemForm,
                                           formset=ImageItemFormset,
                                           can_delete_extra=True)


class UpdateBaseItemForm(forms.ModelForm):
    """
    Form for updating a base item.
    """

    class Meta:
        model = BaseItem
        fields = (
            'description',
            'direction',
            'quantity',
            'price',
            'flavor',
        )
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'direction': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Direction'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Price per item'}),
            'flavor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Flavor'}),
        }

    def clean_flavor(self):
        """
        Custom clean method to check if the flavor already exists in this folder.
        """
        items = self.instance.folder.first().get_items_no_size()
        flavor = self.cleaned_data.get('flavor')
        if items.filter(flavor=flavor).exclude(flavor=self.instance.flavor).exists():
            self.add_error('flavor', 'This flavor already exists in this folder!')
        return flavor


class AddNewSizeForm(forms.ModelForm):
    """
    Form for adding a new size.
    """
    size = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = BaseItem
        fields = (
            'quantity',
            'price',
        )


# flavor forms

class AddNewFlavor(CreateBaseItemForm):
    """
    Form for adding a new flavor.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor to initialize the folder.
        """
        self.folder = kwargs.pop('folder', None)
        super(AddNewFlavor, self).__init__(*args, **kwargs)

    def clean_flavor(self):
        """
        Custom clean method to check if the flavor already exists in this folder.
        """
        items = self.folder.get_items_no_size()
        flavor = self.cleaned_data.get('flavor')
        if items.filter(flavor=flavor).exists():
            self.add_error('flavor', 'This flavor already exists in this folder!')
        return flavor
