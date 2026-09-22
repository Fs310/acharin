from django.urls import path
from . import views, management_views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='homes'),
    path('service', views.service, name='services'),
    path('detail_service/<int:id>', views.detail_service, name='detail_service'),
    path('new', views.new, name='new'),
    path('sub_new/<int:id>', views.new, name='sub_new'),
    path('detail_new/<str:slug>', views.detail_new, name='detail_new'),
    path('search', views.search_results, name='search_results'),
    path('repair', views.clients, name='clients'),
    path('comments', views.comments, name='comments'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),

    path('management/', management_views.management_dashboard, name='management_dashboard'),
    path('management/<str:section>/', management_views.management_list, name='management_list'),
    path('management/<str:section>/add/', management_views.management_form, name='management_create'),
    path('management/<str:section>/<int:pk>/edit/', management_views.management_form, name='management_edit'),
    path('management/<str:section>/<int:pk>/delete/', management_views.management_delete, name='management_delete'),
]
