from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new_image/', views.add_image, name='new_image'),
    path('image/<int:image_id>/', views.set_image, name='image'),
]
