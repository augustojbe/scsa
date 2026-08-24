from base.models import Notification


def notifications(request):
    unread_count = 0
    recent = []
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated and getattr(user, 'brokerage', None):
        queryset = Notification.all_objects.filter(
            brokerage=user.brokerage,
            user=user,
        )
        unread_count = queryset.filter(is_read=False).count()
        recent = queryset[:8]
    return {
        'notifications_unread_count': unread_count,
        'notifications_recent': recent,
    }
