"""yourshelf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from yourshelf import settings
from yourshelf.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup, name="signup"),
    path('pricing/', pricing, name="pricing"),
    path('product/subscription/<uidb64>', product, name="product"),
    path('iyzico_callback/', iyzico_callback, name="iyzico_callback"),
    path('checkout/', checkout, name="checkout"),
    path('profile/', profile, name="profile"),
    path('logout_redirect/', logout_redirect, name="logout_redirect"),
    path('activate/<uidb64>/<token>/',
        activate, name='activate'),
    path('signin/', custom_login, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/logout_redirect'}, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()