"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from apps.restaurants.seo import robots_txt_response, sitemap_xml_response

urlpatterns = [
    path('admin/', admin.site.urls),

    # عمداً در سطح بالای این فایل و قبل از include شدن apps.restaurants.urls
    # قرار گرفته‌اند: آن اپ یک الگوی catch-all دارد (<str:slug>/) که در غیر
    # این صورت می‌توانست 'robots.txt' یا 'sitemap.xml' را به اشتباه به‌عنوان
    # اسلاگ یک رستوران تفسیر کند.
    path('robots.txt', robots_txt_response, name='robots_txt'),
    path('sitemap.xml', sitemap_xml_response, name='sitemap_xml'),

    path('accounts/', include('apps.accounts.urls')),
    path('panel/', include('apps.menu.urls', namespace='menu')),
    path('', include('apps.restaurants.urls')),
]

# در محیط توسعه، فایل‌های media (تصاویر آپلودشده) مستقیماً توسط Django سرو می‌شوند.
# در Production این کار باید توسط Nginx انجام شود.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
