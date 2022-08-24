"""buggy_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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

from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, include
from pages.views import (
    home_view, 
    HomeView, 
    CheckoutView, 
    ItemDetailView, 
    OrderSummaryView,
    support_view,
    search_view,
    summary_remove,
    summary_add,
    summary_remove_all,
    support_requests,
    )

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', home_view, name='home'),
    path('shop/', HomeView.as_view(),name='shop'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('support_requests/', support_requests.as_view(), name='support_requests'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('accounts/', include('allauth.urls')),
    path('support/', support_view.as_view(), name='support'),
    path('search/', search_view, name='search'),
    path('summary_remove/<slug>/', summary_remove, name='summary_remove'),
    path('summary_add/<slug>/', summary_add, name='summary_add'),
    path('summary_remove_all/<slug>/', summary_remove_all, name='summary_remove_all'),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT})
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
