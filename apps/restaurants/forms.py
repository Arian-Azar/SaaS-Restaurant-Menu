from django import forms

from .models import HeroSlide, RestaurantImage, RestaurantStat, Testimonial


class RestaurantImageForm(forms.ModelForm):
    class Meta:
        model = RestaurantImage
        fields = ['image', 'caption', 'sort_order']


class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = ['image', 'title', 'subtitle', 'is_active', 'sort_order']


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['customer_name', 'comment', 'rating', 'avatar', 'is_active', 'sort_order']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class RestaurantStatForm(forms.ModelForm):
    class Meta:
        model = RestaurantStat
        fields = ['label', 'number', 'sort_order']
