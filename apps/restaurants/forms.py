from django import forms

from .models import RestaurantImage


class RestaurantImageForm(forms.ModelForm):
    class Meta:
        model = RestaurantImage
        fields = ['image', 'caption', 'sort_order']
