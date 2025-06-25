from .models import Notification  # Import your Notification model properly

def notification_badge(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications': unread_count}
    return {}
