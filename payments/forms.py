from django import forms

from .models import OrderDetail


class ChangeOrderStatusForm(forms.ModelForm):
    """
    Form for change order status.
    """
    class Meta:
        model = OrderDetail
        fields = (
            'status',
            'ship_number'
        )

        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'ship_number': forms.TextInput(attrs={'class': 'form-control'})
        }
