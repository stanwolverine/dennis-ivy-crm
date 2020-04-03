from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    login_view,
    logout_view,
    register_view,
    account_settings_view,
    home_view,
    user_page_view,
    products_view,
    customer_view,
    create_order_view,
    update_order_view,
    delete_order_view,
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user/', user_page_view, name='user-page'),
    path('account/', account_settings_view, name='account-settings'),

    path('', home_view, name='home'),
    path('products/', products_view, name='products'),
    path('customer/<int:pk>', customer_view, name='customer'),

    path('create_order/<str:pk>/', create_order_view, name='create_order'),
    path('update_order/<str:pk>/', update_order_view, name='update_order'),
    path('delete_order/<str:pk>/', delete_order_view, name='delete_order'),

    path('reset_password/', auth_views.PasswordResetView.as_view(),
         name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

]
