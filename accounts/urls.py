from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_user, name='login'),
    path('registrasion/', views.user_registration, name='user_registration'),
    path('logout/', views.user_logout, name='logout_user'),
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password_reset/', views.custom_password_reset_request, name='password_rest'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path("history/", views.history, name='history'),
    path('detail_history/<int:id>', views.detail_history, name='detail_history'),
    path('submit_review/<int:factor_id>/<int:service_id>', views.submit_review, name='submit_review'),
]
