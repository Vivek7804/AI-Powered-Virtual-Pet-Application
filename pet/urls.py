from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_pet, name='create_pet'),
    path('feed/<int:pet_id>/', views.feed_pet, name='feed_pet'),
    path('play/<int:pet_id>/', views.play_pet, name='play_pet'),
    path('rest/<int:pet_id>/', views.rest_pet, name='rest_pet'),
    path('chat/', views.chat_view, name='chat'),
    path('pets/', views.list_pets, name='list_pets'),
    path('switch/<int:pet_id>/', views.switch_pet, name='switch_pet'),
]
