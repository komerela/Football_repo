"""
URL configuration for fifachampsonline project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf.urls.static import static
from django.conf import settings
from .views import (PlayerDetailView, 
                    PlayerCreateView, 
                    PlayerUpdateView, 
                    PlayerDeleteView, 
                    PlayerListView, 
                    FixtureListView,
                    FixtureDetailView,
                    FixtureCreateView,
                    FixtureUpdateView,
                    FixtureDeleteView,
                    ShopView, 
                    ProfileView,
                    HeadToHeadView,
                    HeadToHeadRequestView, 
                    RestrictedView,
                    HomeView,
                    error_view,
                    player_info,
                    cart_view,
                    add_to_cart,
                    item_detail,)

app_name = 'fixtures'

# Define a function to check if the user is staff
def user_is_staff(user):
    return user.is_staff

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', HomeView.as_view(), name='home'),
    path('restricted/', user_passes_test(user_is_staff)(RestrictedView.as_view()), name='restricted-view'),
    path('fixture/', FixtureListView.as_view(), name='fixture-list'),
    path('fixture/<int:fixture_id>/', FixtureDetailView.as_view(), name='fixture-detail'),
    path('fixture/add/', login_required(FixtureCreateView.as_view()), name='fixture-create'),
    path('fixture/<int:fixture_id>/update/', login_required(FixtureUpdateView.as_view()), name='fixture-update'),
    path('fixture/<int:fixture_id>/delete/', user_passes_test(user_is_staff)(FixtureDeleteView.as_view()), name='fixture-delete'),
    path('head-to-head/<int:id>/', HeadToHeadView.as_view(), name='head_to_head'),
    path('head-to-head-request/', HeadToHeadRequestView.as_view(), name='head_to_head_request'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('item/<int:pk>/', item_detail, name='item_detail'),
    path('cart/', cart_view, name='cart'),
    path('shop/<int:item_id>/add_to_cart/', add_to_cart, name='add_to_cart'),
    path('process_payment/<int:item_id>/', views.process_payment, name='process_payment'),
    path('payment_success/', views.process_payment, name='payment_success'),
    path('payment_error/', views.payment_error, name='payment_error'),
    path('shop/<int:item_id>/purchase/', views.purchase_item, name='purchase_item'),
    path('players/', login_required(PlayerListView.as_view()), name='player-list'),
    path('players/<int:pk>/', login_required(PlayerDetailView.as_view()), name='player-detail'),
    path('players/create/', login_required(PlayerCreateView.as_view()), name='player-create'),
    path('players/<int:pk>/update/', user_passes_test(user_is_staff)(PlayerUpdateView.as_view()), name='player-update'),
    path('players/<int:pk>/delete/', user_passes_test(user_is_staff)(PlayerDeleteView.as_view()), name='player-delete'),
    path('players/<int:player_id>/', player_info, name='player-info'),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('error/', error_view, name='error'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)