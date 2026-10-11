from .models import ActivityLog


def log_activity(user, action, object_type, obj=None, title=None):
    """Record a user action. `obj` is optional for account-level events."""
    ActivityLog.objects.create(
        user=user,
        action=action,
        object_type=object_type,
        object_id=getattr(obj, "pk", None),
        object_title=(title or getattr(obj, "title", "") or "")[:200],
    )
