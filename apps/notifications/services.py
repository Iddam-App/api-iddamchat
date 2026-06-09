from .models import Notification


def create_notification(*, recipient, sender, notification_type, message,
                        content_type='', content_id=None):
    """Create a notification. Skips if sender == recipient."""
    if recipient == sender:
        return None
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        content_type=content_type,
        content_id=content_id,
        message=message,
    )
