from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from .forms import RestaurantRegistrationForm
from .services import register_restaurant_owner


class RestaurantRegisterView(View):
    """
    View ثبت‌نام رستوران جدید.

    منطق واقعی ساخت User+Restaurant در apps/accounts/services.py است؛
    این View فقط مسئول اعتبارسنجی فرم، فراخوانی سرویس، و مدیریت خطای
    غیرمنتظره (مثلاً یک IntegrityError نادر) است.
    """

    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name, {'form': RestaurantRegistrationForm()})

    def post(self, request):
        form = RestaurantRegistrationForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        data = form.cleaned_data
        try:
            user, _restaurant = register_restaurant_owner(
                username=data['username'],
                password=data['password'],
                restaurant_name=data['restaurant_name'],
                email=data.get('email', ''),
                phone_number=data.get('phone_number', ''),
                full_name=data.get('full_name', ''),
            )
        except Exception:
            # هر خطای غیرمنتظره‌ی دیگر (مثلاً مشکل پایگاه‌داده) اینجا گرفته می‌شود
            # تا کاربر پیام فارسی مناسب ببیند، نه یک 500 خام.
            form.add_error(None, 'خطایی در ثبت‌نام رخ داد. لطفاً دوباره تلاش کنید.')
            return render(request, self.template_name, {'form': form})

        login(request, user)
        return redirect('dashboard')


class RestaurantOwnerLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return str(reverse_lazy('dashboard'))


class RestaurantOwnerLogoutView(LogoutView):
    next_page = reverse_lazy('login')
