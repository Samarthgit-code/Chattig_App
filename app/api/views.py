from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message,Notification
from .forms import MessageForm
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.cache import cache

@csrf_exempt
@login_required
def update_typing_status(request, username):
    cache.set(f"{request.user.username}_typing_to_{username}", timezone.now(), timeout=5)
    return JsonResponse({'status': 'ok'})


@login_required(login_url="login")
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    for user in users:
        user.unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
            message__icontains=user.username  # assuming message contains sender's username
        ).count()
    return render(request, 'user_list.html', {'users': users})

@login_required(login_url="login")
def chat_view(request, username):
    other_user = User.objects.get(username=username)
    receiver = User.objects.get(username=username)
    Notification.objects.filter(
        user=request.user,
        is_read=False,
        message__icontains=other_user.username
    ).update(is_read=True)

    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other_user
            msg.save()
            Notification.objects.create(
            user=receiver,
            message=f"New message from {request.user.username}"
        )
            return redirect('chat', username=other_user.username)
    else:
        form = MessageForm()

    return render(request, 'chat.html', {'form': form, 'messages': messages, 'other_user': other_user})


def Login(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")

        user=authenticate(username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect("home")

    return render(request,"login.html")

def Register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already taken"})

        user = User.objects.create_user(username=username, email=email, password=password)
        return redirect("login")  

    return render(request, "register.html")


def Logout(request):
    logout(request)
    return redirect('home')


def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'notifications.html', {'notifications': notifications})
