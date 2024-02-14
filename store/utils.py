from django.http import Http404

from .models import BaseItem


class SortMixin(object):
    """
    Mixin for sort items by price, for this mixin need sort_by_price.html in template
    """

    def get_sort_operation(self):
        return self.request.POST.get('sort', 'up')

    def get_items(self):
        """
        Checking if an object having items' field or object is BaseItem
        """
        object = self.get_object()
        if BaseItem is object:
            return object.single_item
        elif hasattr(object, 'items'):
            return object.items.all()
        return Http404

    def get_queryset(self):
        """
        The method is updating queryset by order operation and return queryset.
        """
        sort_op = self.get_sort_operation()
        items = self.get_items()
        if sort_op == 'down':
            queryset = items.order_by('price')
        else:
            queryset = items.order_by('-price')
        return queryset

    def sort_items(self, queryset, ordering='price'):
        """
        Return sorted items by price form queryset
        """
        sort_op = self.get_sort_operation()
        if sort_op == 'down':
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-' + ordering)
        return queryset

    def update_context(self, context):
        """
        Use in view to update context for include sort_by_price.html.
        """
        context['current_sort'] = self.get_sort_operation()
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()  # in case if view having paginator
        return self.render_to_response(context=self.get_context_data())
