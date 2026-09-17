from django import forms

from .models import (
    BlogPost,
    HeroSlide,
    Reservation,
    RestaurantImage,
    RestaurantStat,
    TeamMember,
    Testimonial,
)


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


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'position', 'photo', 'instagram', 'is_active', 'sort_order']


class ReservationForm(forms.ModelForm):
    """
    فرم عمومی رزرو میز — روی صفحه‌ی عمومی رستوران (بدون نیاز به لاگین) نمایش
    داده می‌شود. برخلاف فرم دمو تمپلیت (action="#")، این فرم واقعاً رزرو را
    در دیتابیس ثبت می‌کند.
    """

    class Meta:
        model = Reservation
        fields = ['customer_name', 'phone_number', 'email', 'party_size', 'reservation_date', 'reservation_time', 'note']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام شما'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09xxxxxxxxx'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل (اختیاری)'}),
            'party_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reservation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reservation_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'image', 'content', 'is_published']
