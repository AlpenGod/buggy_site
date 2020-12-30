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

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, include
from pages.views import (
    home_view, 
    xss_view, 
    HomeView, 
    CheckoutView, 
    ItemDetailView, 
    OrderSummaryView,
    support_view,
    search_view,
    xxe_view,
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),
    path('xss/', xss_view.as_view()),
    path('shop/', HomeView.as_view(),name='shop'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('accounts/', include('allauth.urls')),
    path('support/', support_view.as_view()),
    path('search/', search_view),
    path('xxe/', xxe_view),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    #jakby cos sie ze staticem tez psulo to zamien MEDIA_ROOT i MEDIA_URL na STATIC w newline i bd gituwa