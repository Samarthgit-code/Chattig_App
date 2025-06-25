from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
path('profile/<str:username>/update', views.update_profile_picture, name='picture'),
path('profile/<str:username>/update-banner/', views.update_banner, name='update_banner'),
path('media-proxy/<path:path>/', views.proxy_nextcloud_file, name='media-proxy'),

path('',views.index,name='home'),
path('video/<int:video_id>/comments', views.show_comments, name='show_comments'),

  path('history/', views.watch_history, name='watch_history'),
path('view',views.view_data),
path('create',views.create,name='create'),
path('create_post',views.create_post,name='create_post'),

path('video/<int:video_id>/comments', views.show_comments, name='show_comments'),

path('profile/<str:username>/',views.profile,name='profile'),
path('logout',views.Logout ,name='logout'),
path('login',views.Login,name='login'),
path('following/<str:username>/',views.following,name='following'),
path('video/<int:video_id>/', views.video_detail, name='video_detail'), 

path('shorts', views.shorts, name='shorts'), 

path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
path('video/<int:video_id>/like/', views.like_dislike_video, {'action': 'like'}, name='video_like'),
path('video/<int:video_id>/dislike/', views.like_dislike_video, {'action': 'dislike'}, name='video_dislike'),

path('post/<int:post_id>/<str:action>/', views.like_dislike_post, name='like_dislike_post'),

path('notifications', views.notifications_view, name='notifications'),
path('unread_notifications', views.notification_badge, name='unread_notifications'),    
path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),






path('create',views.create),
path('user/<str:username>/', views.view_profile, name='view_profile'),
path('subscribe/<str:username>/', views.subscribe, name='subscribe'),
path('unsubscribe/<str:username>/', views.unsubscribe, name='unsubscribe'),

path('profile/<str:username>/edit/', views.update_profile_view, name='update_profile_view'),

path('profile/<str:username>/update/', views.update_profile, name='update_profile'),



path('videos/<int:video_id>/delete/', views.delete_video, name='delete_video'),




path('signup',views.signup,name='signup'),
path('500',views.custom_500,name='500'),





path("upload_profile",views.upload_profile, name="upload_profile")
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)