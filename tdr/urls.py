from django.conf.urls import include
from django.contrib import admin
from django.urls import path

import sites

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sites/', include('sites.urls')),
    path('accounts/', include('accounts.urls')),
    path('', sites.views.home, name='home'),
    path('about', sites.views.about, name='about'),
    path('rules', sites.views.rules, name='rules'),
]


