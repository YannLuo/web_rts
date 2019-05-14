"""web_rts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path
from rts import views as rts_views

urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"rts/", rts_views.index),
    re_path(r"results/[a-zA-Z\_0-9]+/[0-9a-f]{7}/[a-zA-Z\_0-9]+/", rts_views.show_result),
    re_path(r"$^", rts_views.index)
]
