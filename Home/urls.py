from django.urls import path
from . import views

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

]
