from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class RestaurantRegistrationForm(forms.Form):
    """
    فرم ترکیبی ثبت‌نام: هم اطلاعات User و هم نام Restaurant را می‌گیرد،
    چون طبق فرآیند تعریف‌شده در پروپوزال، این دو باید همزمان و اتمیک
    ساخته شوند (به apps/accounts/services.py نگاه کن).
    """

    restaurant_name = forms.CharField(label='نام رستوران/کافه', max_length=150)
    full_name = forms.CharField(label='نام و نام‌خانوادگی مالک', max_length=150, required=False)
    username = forms.CharField(label='نام کاربری', max_length=150)
    email = forms.EmailField(label='ایمیل', required=False)
    phone_number = forms.CharField(label='شماره موبایل', max_length=20, required=False)
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='تکرار رمز عبور', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('این نام کاربری قبلاً استفاده شده است.')
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        # از همان اعتبارسنج‌های استاندارد جنگو استفاده می‌کنیم
        # (طول کافی، شباهت زیاد به نام کاربری، رمز رایج و ... — در base.py تعریف شده).
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password_confirm = cleaned.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'رمز عبور و تکرار آن یکسان نیستند.')
        return cleaned
