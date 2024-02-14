from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import generic
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect

from .models import Animal, BaseItem, ItemFolder, Category
from .permissions import IsAdmin
from .utils import SortMixin

import json

import store.forms as forms


# item folder

class CreateItemFolderView(LoginRequiredMixin, IsAdmin, generic.CreateView):
    """
    View for creating folder of items
    """
    form_class = forms.CreateItemFolderForm
    template_name = 'store/create_item_folder.html'

    def get_success_url(self):
        return redirect(reverse('my_folders'))

    def form_valid(self, form):
        """
        Override the behavior of the form to store an owner of the item.
        """
        form = form.save(commit=False)
        form.owner = self.request.user
        form.save()
        return self.get_success_url()


class MyFoldersView(LoginRequiredMixin, IsAdmin, generic.ListView):
    """
    Show folder for current user.
    """
    template_name = 'store/my_folder.html'
    context_object_name = 'folders'
    allow_empty = False

    def get_queryset(self):
        queryset = self.request.user.folders
        return queryset


class FolderDetailView(LoginRequiredMixin, IsAdmin, generic.DetailView):
    """
    Showing the current folder from slug.
    """
    model = ItemFolder
    context_object_name = 'folder'
    template_name = 'store/folder_detail.html'
    slug_url_kwarg = 'folder_slug'


class DeleteFolderView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    """
    Delete folder and all items in it.
    """
    model = ItemFolder

    def get_success_url(self):
        return redirect(reverse('my_folders'))

    def get_folder(self):
        folder = get_object_or_404(ItemFolder, slug=self.kwargs.get('folder_slug'))
        return folder

    def post(self, request, *args, **kwargs):
        folder = self.get_folder()
        folder.delete()
        return self.get_success_url()

    def test_func(self):
        """
        Check if the current user is an owner of the folder.
        """
        return self.request.user.is_staff and self.get_folder().owner == self.request.user


# Store/items

class StoreView(SortMixin, generic.ListView):
    """
    Showing all items on the home page.
    """
    template_name = 'index.html'
    model = BaseItem
    context_object_name = 'items'
    paginate_by = 8

    def get_object(self):
        return BaseItem

    def get_context_data(self, *args, **kwargs):
        context = super(StoreView, self).get_context_data(*args, **kwargs)
        context['animals'] = Animal.objects.all()
        return self.update_context(context=context)


class ShowCategoryByAnimal(SortMixin, generic.DetailView):
    """
    This view is sorting item by animal type.
    """
    template_name = 'store/category.html'
    model = Animal
    context_object_name = 'animal'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        return get_object_or_404(Animal, slug=self.kwargs.get('slug'))

    def get_page_number(self):
        page = self.request.GET.get('page', None)
        return page

    def get_context_data(self, **kwargs):
        context = dict()
        paginator = Paginator(self.get_queryset(), 8)
        page = paginator.page(self.get_page_number() or 1)
        context['animal'] = self.get_object()
        context['paginator'] = paginator
        context['items'] = page
        context['page_obj'] = page
        context['type_of_food'] = Category.objects.all()
        return self.update_context(context=context)


class ShowCategoryByTypeOfFood(SortMixin, generic.ListView):
    """
    This view is sorting item by animal type and food type.
    """
    template_name = 'store/category.html'
    context_object_name = 'items'
    paginate_by = 8

    def get_object(self, queryset=None):
        return get_object_or_404(Animal, slug=self.kwargs.get('animal_slug'))

    def get_type_of_food_slug(self):
        return self.kwargs.get('type_food_slug')

    def get_queryset(self):
        return self.sort_items(self.get_object().items.filter(type_of_food__slug=self.get_type_of_food_slug()))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['type_of_food'] = Category.objects.all()
        context['animal'] = self.get_object()
        context['current_type'] = self.get_type_of_food_slug()
        return self.update_context(context=context)


class ItemDetailView(generic.detail.SingleObjectMixin, generic.detail.SingleObjectTemplateResponseMixin, generic.View):
    """
    Showing item from pk and all his sizes and flavors.
    """
    template_name = 'store/detail_item.html'

    def get_object(self, queryset=None):
        """
        Get an item and check if it exists.
        """
        item_pk = self.kwargs.get('pk')
        item = get_object_or_404(BaseItem, pk=item_pk)
        return item

    def get_context_data(self, **kwargs):
        context = dict()
        context['item'] = self.get_object()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        item = self.get_object()
        folder_slug = self.kwargs.get('folder_slug')
        if item.item_folder.slug != folder_slug:  # check if folder slug is correct (we need folder for flavors)
            return HttpResponseRedirect(
                reverse('detail_item', kwargs={'folder_slug': item.item_folder.slug, 'pk': item.pk}))
        return self.render_to_response(context=context)


class NewBaseItemView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    form_class = forms.CreateBaseItemForm
    template_name = 'store/new_base_item.html'

    def get_item_folder(self):
        folder = get_object_or_404(ItemFolder, slug=self.kwargs.get('folder_slug'))
        if folder.items.all().exists():
            """
            Check if folder doesn't have items, because one folder can have one item,
            but with different sizes and flavors.
            """
            raise Http404
        return folder

    def get_context_data(self, **kwargs):
        """
        Add formset to add many images.
        """
        context = super().get_context_data(**kwargs)
        context['images_form'] = forms.image_formset
        return context

    def save_images(self, images_form, item):
        """
        Save images to current item
        """
        images = images_form.save(commit=False)
        for image in images:
            image.base_item = item
            image.save()

    def post(self, request, *args, **kwargs):
        """
        Override post-method to save form for current user and save images.
        """
        form = forms.CreateBaseItemForm(self.request.POST)
        images_form = forms.image_formset(self.request.POST, self.request.FILES, )
        folder = self.get_item_folder()
        if form.is_valid() and images_form.is_valid():
            item = form.save(commit=False)
            item.owner = self.request.user
            item.item_folder = folder
            item.save()
            item.sizes.add(item)
            folder.flavors.add(item)
            self.save_images(images_form=images_form, item=item)
            return HttpResponseRedirect(reverse('detail_item', kwargs={'folder_slug': folder.slug, 'pk': item.pk}))
        return self.render_to_response(context={'form': form, 'images_form': images_form})

    def test_func(self):
        return self.request.user.is_staff and self.get_item_folder().owner == self.request.user


class AddSizeFood(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    """
    Add new size for item
    """
    template_name = 'store/add_size.html'

    def get_item(self):
        item = get_object_or_404(BaseItem, pk=self.kwargs.get('pk'))
        return item

    def get_context_data(self, **kwargs):
        context = dict()
        context['form'] = forms.AddSizeFoodForm
        context['images_form'] = forms.image_formset
        return context

    def save_images(self, images_form, item):
        images = images_form.save(commit=False)
        for image in images:
            image.base_item = item
            image.save()

    def post(self, request, *args, **kwargs):
        """
        Create a copy of item we are going add size and save forms
        """
        copy_item = self.get_item()
        item_folder = copy_item.folder.first()
        copy_item.pk = None
        copy_item.save()
        form = forms.AddSizeFoodForm(self.request.POST, instance=copy_item, parent_item=self.get_item())
        images_form = forms.image_formset(self.request.POST, self.request.FILES, )
        if form.is_valid() and images_form.is_valid():
            item = form.save(commit=False)
            item.save()
            parent_item = self.get_item()
            parent_item.sizes.add(item)
            item_folder.flavors.add(item)
            self.save_images(images_form=images_form, item=item)
            return redirect(item.get_absolute_url())
        return self.render_to_response(context={'form': form, 'images_form': images_form})

    def test_func(self):
        return self.request.user.is_staff and self.get_item().owner == self.request.user


class UpdateBaseItemView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    """
    Update item data
    """
    form_class = forms.UpdateBaseItemForm
    template_name = 'store/update_base_item.html'

    def get_object(self):
        return get_object_or_404(BaseItem, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        base_item = self.get_object()
        context = {
            'form': forms.UpdateBaseItemForm(instance=base_item),
        }
        return context

    def get_success_url(self):
        obj = self.get_object()
        return redirect(
            reverse('detail_item', kwargs={'folder_slug': obj.item_folder.slug, 'pk': self.get_object().pk}))

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        form = forms.UpdateBaseItemForm(self.request.POST, instance=obj)

        if form.is_valid():
            form.save()
            return self.get_success_url()
        return self.render_to_response(context={'form': form})

    def test_func(self):
        return self.request.user.is_staff and self.get_object().owner == self.request.user


class DeleteItemView(LoginRequiredMixin, UserPassesTestMixin, generic.View):
    def get_item(self):
        item = get_object_or_404(BaseItem, pk=self.kwargs.get('pk', None))
        return item

    def post(self, request, *args, **kwargs):
        item = self.get_item()
        folder_slug = item.item_folder.slug
        item.sizes.all().delete()
        item.delete()
        return redirect(reverse('detail_folder', kwargs={'folder_slug': folder_slug}))

    def test_func(self):
        return self.request.user.is_staff and self.get_item().owner == self.request.user


# flavor

class AddNewFlavorView(LoginRequiredMixin, UserPassesTestMixin, generic.FormView):
    """
    Add new flavor to item.
    """
    form_class = forms.AddNewFlavor
    template_name = 'store/new_base_item_flavor.html'

    def get_folder(self):
        return get_object_or_404(ItemFolder, slug=self.kwargs.get('folder_slug'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images_form'] = forms.image_formset
        return context

    def get_success_url(self):
        return redirect(reverse('detail_folder', kwargs={'folder_slug': self.kwargs.get('folder_slug')}))

    def post(self, request, *args, **kwargs):
        folder = self.get_folder()
        form = forms.AddNewFlavor(self.request.POST, folder=folder)
        images_form = forms.image_formset(self.request.POST, self.request.FILES)
        if form.is_valid() and images_form.is_valid():
            form = form.save(commit=False)
            form.item_folder = folder
            form.owner = self.request.user
            form.save()
            folder.flavors.add(form)
            form.sizes.add(form)
            images = images_form.save(commit=False)
            for image in images:
                image.base_item = form
                image.save()
            return self.get_success_url()
        return self.render_to_response(context={'form': form, 'images_form': images_form})

    def test_func(self):
        return self.request.user.is_staff and self.get_folder().owner == self.request.user


# search

class SearchBaseItemView(SortMixin, generic.ListView):
    """
    Search from user input
    """
    model = BaseItem
    template_name = 'store/search_list.html'
    context_object_name = 'items'
    paginate_by = 8

    def get_queryset(self):
        """
        Filter the result from a database.
        """
        query = self.request.GET.get('q')
        items = BaseItem.single_item.filter(
            Q(name__icontains=query) | Q(type_of_food__name__icontains=query) | Q(animal__name__icontains=query) | Q(
                flavor__icontains=query)
        )
        return self.sort_items(items)

    def get_context_data(self, *args, **kwargs):
        context = super(SearchBaseItemView, self).get_context_data(*args, **kwargs)
        context['search_name'] = self.request.GET.get('q')
        return self.update_context(context=context)


class SearchBaseItemSuggestionView(generic.ListView):
    """
    View to show a suggestion while user typing something.
    """
    model = BaseItem
    template_name = 'store/search_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        query = self.request.GET.get('q')
        items = BaseItem.single_item.filter(
            Q(name__icontains=query) | Q(type_of_food__name__icontains=query) | Q(animal__name__icontains=query) | Q(
                flavor__icontains=query)
        )[:5]
        return items

    def get(self, request, *args, **kwargs):
        """
        Send JSON data back to user.
        """
        return HttpResponse(json.dumps({'data': [item.name for item in self.get_queryset()]}))
