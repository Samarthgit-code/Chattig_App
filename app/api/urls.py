from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='home'),
    path('chat/<str:username>/', views.chat_view, name='chat'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),    
    path('typing/<str:username>/', views.update_typing_status, name='typing_status'),

    path('register', views.Register, name='register'),


]
