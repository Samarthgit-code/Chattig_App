from datetime import datetime
import time
import os
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from .models import LikeDislike, Notification, PostLikeDislike, Posts, Profile,Videos,Comment, WatchHistory
from .form import CommentForm, ProfileForm, VideoUploadForm,RegisterForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.core.files.storage import default_storage
# Create your views here.

import requests
from django.conf import settings
from django.http import HttpResponse

def proxy_nextcloud_file(request, path):
    url = settings.NEXTCLOUD_BASE_URL + path
    response = requests.get(url, auth=(settings.NEXTCLOUD_USERNAME, settings.NEXTCLOUD_PASSWORD))

    if response.status_code == 200:
        return HttpResponse(response.content, content_type=response.headers.get('Content-Type'))
    return HttpResponse("File not found", status=404)


@login_required(login_url='login')
def subscribe(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.user.profile != target_user.profile:
        request.user.profile.subscriptions.add(target_user.profile)
        notification=Notification.objects.create(user=target_user,message=f"Subscribed to your profile: {request.user}")
        notification.save()
    return HttpResponseRedirect(reverse('profile', args=[username]))   

def custom_500(request):
    return render(request,'pages/error-500.html') 

@login_required
def unsubscribe(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.user.profile != target_user.profile:
        request.user.profile.subscriptions.remove(target_user.profile)
        notification=Notification.objects.create(user=target_user,message=f"Unsubscribed to your profile: {request.user}")   
        notification.save()
    return HttpResponseRedirect(reverse('profile', args=[username]))


@login_required(login_url='login')
def view_profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    print(user_profile)
    if user_profile is None:
        return render(request,'error-500.html')
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = user_profile.profile in request.user.profile.subscriptions.all()
    return render(request, 'pages/basic_elements.html', {
        'user_profile': user_profile,
        'is_subscribed': is_subscribed,
        
    })



@login_required(login_url='login')
def upload_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'success')
            return redirect(request,'')
        
            
    else:
        form = ProfileForm()
    return redirect(request, '')


@login_required(login_url='login')
def view_data(request):
    video=Videos.objects.all()
    return render(request,"view.html",{'videos':video,'nextcloud_base': settings.NEXTCLOUD_PUBLIC_BASE,})



@login_required(login_url='login')
def index(request):
    videos = Videos.objects.all().prefetch_related('comments', 'user__profile')
    return render(request, "pages/basic_elements.html", {'videos': videos,'nextcloud_base': settings.NEXTCLOUD_PUBLIC_BASE})
    

from django.db.models import Count, Q

@login_required(login_url='login')
def profile(request, username):
    user_profile = get_object_or_404(User, username=username)

    is_subscribed = user_profile.profile in request.user.profile.subscriptions.all()
    
    subscriptions = user_profile.profile.subscriptions.all()
    videos = Videos.objects.all()
    
    # Annotate posts with like and dislike count
    posts = Posts.objects.annotate(
        like_count=Count('likes_dislikes', filter=Q(likes_dislikes__value='like')),
        dislike_count=Count('likes_dislikes', filter=Q(likes_dislikes__value='dislike'))
    ).order_by('-uploaded_at')

    # Add user_action per post
    for post in posts:
        user_like = PostLikeDislike.objects.filter(post=post, user=request.user).first()
        post.user_action = user_like.value if user_like else None

    return render(request, 'pages/blank.html', {
        'user_profile': user_profile,

        'is_subscribed': is_subscribed,
        'subscriptions': subscriptions,
        'videos': videos,
        'posts': posts,
    })
@login_required(login_url='login')
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'pages/notifications.html', {'notifications': notifications})

@login_required(login_url='login')
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('notifications')  

@login_required(login_url='login')
def notification_badge(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications': unread_count}
    return {}

@login_required
def like_dislike_video(request, video_id, action):
    video = get_object_or_404(Videos, id=video_id)
    like_obj, created = LikeDislike.objects.get_or_create(user=request.user, video=video)

    if action == 'like':
        like_obj.value = 'like'
        notification=Notification.objects.create(user=video.user,message=f"Liked to Video: {video.title} : {request.user}")
        notification.save()
    elif action == 'dislike':
        like_obj.value = 'dislike'
        notification=Notification.objects.create(user=video.user,message=f"Disliked to Video: {video.title} : {request.user}")
        notification.save()
    like_obj.save()

    return redirect('video_detail', video_id=video.id)


@login_required
def like_dislike_post(request, post_id, action):
    post = get_object_or_404(Posts, id=post_id)
    like_obj, created = PostLikeDislike.objects.get_or_create(user=request.user, post=post)
    print(action)
    if action == 'like':
        like_obj.value = 'like'
        notification=Notification.objects.create(user=post.user,message=f"Liked to Post: {post.caption} : {request.user}")
        notification.save()
    elif action == 'dislike':
        like_obj.value = 'dislike'
        notification=Notification.objects.create(user=post.user,message=f"Disliked to Post: {post.caption} : {request.user}")
        notification.save()

    like_obj.save()

    return redirect('profile',username=post.user.username)
    
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == request.user or request.user.is_superuser:
        video_id = comment.video.id  # Assuming Comment has a ForeignKey to Video
        comment.delete()
        return redirect('video_detail', video_id=video_id)
    else:
        return redirect('video_detail', video_id=comment.video.id)
    
def Login(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")

        user=authenticate(username=username,password=password)

        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse('home'))




    return render(request,"pages/login.html")

@login_required(login_url='login')
def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))



@login_required(login_url='login')
def following(request,username):
    user_profile = get_object_or_404(User, username=username)
    subscriptions = user_profile.profile.subscriptions.all() 
    return render(request,"pages/basic-table.html",{'subscriptions': subscriptions,})



from app.nextcloud_storage import NextcloudWebDAVStorage  # your custom storage class
def signup(request):
    if request.method == "POST":
        # Create the user
        user = User.objects.create_user(
            username=request.POST.get("username"),
            email=request.POST.get("email"),
            password=request.POST.get("password")
        )

        # Initialize custom storage
        storage = NextcloudWebDAVStorage()

        # Handle photo upload
        photo_file = request.FILES.get("photo")
        banner_file = request.FILES.get("banner_image")

        photo_path = storage.save(f"profile_photos/{photo_file.name}", photo_file) if photo_file else None
        banner_path = storage.save(f"profile_banners/{banner_file.name}", banner_file) if banner_file else None

        # Create the profile
        Profile.objects.create(
            user=user,
            bio=request.POST.get("bio"),
            photo=photo_path,
            banner_image=banner_path
        )

        return HttpResponseRedirect(reverse('login'))

    return render(request, "pages/register.html")




@login_required(login_url='login')
def shorts(request):
    videos=Videos.objects.all()
    return render(request,"pages/shorts.html",{'videos':videos})

def format_views(count):
    count = int(count)
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M".rstrip('0').rstrip('.')
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K".rstrip('0').rstrip('.')
    return str(count)


@login_required
def video_detail(request, video_id):
    video = get_object_or_404(Videos, id=video_id)
    videos =Videos.objects.all()

    comments = video.comments.all()
    
    like_count = LikeDislike.objects.filter(video=video, value='like').count()
    dislike_count = LikeDislike.objects.filter(video=video, value='dislike').count()

    # Handle comment submission
    if request.method == 'POST' and 'comment_submit' in request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.video = video
            comment.save()
            notification=Notification.objects.create(user=video.user,message=f" Comment to You for :{video.title}: " +request.POST.get("text") +f": {request.user}")
            notification.save()

    else:
        form = CommentForm()

    if request.user.is_authenticated:
        WatchHistory.objects.create(user=request.user, video=video).save()
        if not video.viewers.filter(id=request.user.id).exists():
            video.views += 1
            video.save()
            video.viewers.add(request.user)

    else:
        pass
    formatted_views = format_views(video.views)

    user_action = None
    if request.user.is_authenticated:
        try:
            user_action = LikeDislike.objects.get(video=video, user=request.user).value
        except LikeDislike.DoesNotExist:
            user_action = None


    context = {
        'video': video,
        'videos': videos,
        'views':formatted_views,
        'comments': comments,
        'form': form,
        'like': like_count,
        'dislike': dislike_count,
        'user_action': user_action,


        
    }
    return render(request, 'pages/video_detail.html', context)

def show_comments(request, video_id):
    print(f"show_comments called for video_id={video_id}")
    video = get_object_or_404(Videos, id=video_id)
    comments = video.comments.all()     

    context = {    
        'video': video,
        'comments': comments,
    }
    return render(request, 'pages/show_comments.html', context)


@login_required(login_url='login')
def create(request):
    if request.method == 'POST':
        title = request.POST.get("title")
        video_file = request.FILES.get("video_file")
        thumbnail = request.FILES.get("thumbnail")
        caption = request.POST.get("caption")

        if title and video_file:
            storage = NextcloudWebDAVStorage()

            # Generate unique filenames
            video_path = f"videos/{request.user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{video_file.name}"
            thumb_path = f"thumbnails/{request.user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{thumbnail.name}"

            # Save to Nextcloud
            saved_video_path = storage.save(video_path, video_file)
            saved_thumb_path = storage.save(thumb_path, thumbnail)

            # Create video entry
            Videos.objects.create(
                user=request.user,
                title=title,
                caption=caption,
                comment="nice",
                uploaded_at=timezone.now(),
                video=saved_video_path,
                tumbnail=saved_thumb_path,
            )

            return redirect('home')

    return render(request, 'pages/create.html')



@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        caption = request.POST.get("caption")
        image = request.FILES.get("image")

        if caption and image:
            try:
                post = Posts.objects.create(
                    user=request.user,
                    caption=caption,
                    uploaded_at=timezone.now(),
                    image=image
                )
                post.save()
                return redirect('home')
            except Exception as e:
                return render(request, 'pages/create_post.html', {
                    'error': f"Upload failed: {str(e)}"
                })
        else:
            return render(request, 'pages/create_post.html', {
                'error': "Both caption and image are required."
            })

    return render(request, 'pages/create_post.html')

@login_required(login_url='login')
def update_profile_view(request,username):
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(Profile, user=user)

    return render(request, 'pages/update_profile.html', {'user': user,'user_profile':user_profile})

@login_required(login_url='login')
def update_profile_picture(request, username):    
    user = get_object_or_404(User, username=username)

    if request.method == 'POST' and request.user == user:
        profile = user.profile

        if 'photo' in request.FILES:
            uploaded_file = request.FILES['photo']

            # Generate a unique filename with timestamp
            filename = f"profile_photos/{user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"

            # Use custom Nextcloud storage
            storage = NextcloudWebDAVStorage()

            # Save file to Nextcloud
            saved_path = storage.save(filename, uploaded_file)

            # Assign to profile
            profile.photo.name = saved_path
            profile.save()

        return redirect('profile', username=username)

    return redirect('profile', username=username)

@login_required(login_url='login')
def update_banner(request, username):
    user = get_object_or_404(User, username=username)

    if request.method == 'POST' and request.user == user:
        profile = user.profile
        if 'banner_image' in request.FILES:
            profile.banner_image = request.FILES['banner_image']
            profile.save()
        return redirect('profile', username=username)

    return redirect('profile', username=username)


@login_required(login_url='login')
def update_profile(request,username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        messages.error(request, "You are not allowed to edit this profile.")
        return redirect('profile', username=user.username)

    profile = user.profile

    if request.method == 'POST':
        # Update User fields
        new_username = request.POST.get('username')
        email = request.POST.get('email')

        if new_username:
            user.username = new_username
        if email:
            user.email = email
        user.save()

        # Update Profile fields
        profile.bio = request.POST.get('bio', profile.bio)
        

        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('profile', username=user.username)

    return render(request, 'profile/update_profile.html', {'user': user, 'profile': profile})


@login_required(login_url='login')
def delete_video(request, video_id):
    video = get_object_or_404(Videos, id=video_id)

    if video.user != request.user:
        return redirect('profile', username=request.user.username)

    if request.method == 'POST':
        # Get video and thumbnail paths for deletion
        video_name = video.video.name
        thumbnail_name = video.tumbnail.name

        try:
            # Delete the DB record
            video.delete()

            # Delete the video file from Nextcloud
            video_url = f"{settings.NEXTCLOUD_BASE_URL}{video_name}"
            thumbnail_url = f"{settings.NEXTCLOUD_BASE_URL}{thumbnail_name}"

            # Delete video file
            video_res = requests.delete(video_url, auth=(settings.NEXTCLOUD_USERNAME, settings.NEXTCLOUD_PASSWORD))
            if video_res.status_code not in [204, 404]:
                print("Failed to delete video file:", video_res.status_code, video_res.text)

            # Delete thumbnail
            if thumbnail_name:
                thumb_res = requests.delete(thumbnail_url, auth=(settings.NEXTCLOUD_USERNAME, settings.NEXTCLOUD_PASSWORD))
                if thumb_res.status_code not in [204, 404]:
                    print("Failed to delete thumbnail:", thumb_res.status_code, thumb_res.text)

        except Exception as e:
            print("Error during video deletion:", e)

        return redirect('profile', username=request.user.username)

    return redirect('profile', username=request.user.username)

@login_required
def watch_history(request):
    history = WatchHistory.objects.filter(user=request.user).select_related('video')
    return render(request, 'pages/watch_history.html', {'history': history})
