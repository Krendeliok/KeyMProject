from django_filters import rest_framework as filters

from .models import UserNotification, NotificationCategory

STATUS_CHOICES = (
    (0, "Not Seen"),
    (1, "Seen"),
)

NOTIFICATION_TYPES = (
    (1, "System"),
    (2, "Push"),
)


class NotificationFilterBackend(filters.FilterSet):
    status = filters.ChoiceFilter(choices=STATUS_CHOICES)
    notification_type = filters.ChoiceFilter(choices=NOTIFICATION_TYPES)
    notification_category = filters.ModelMultipleChoiceFilter(
        field_name="notification_template__notification_category",
        queryset=NotificationCategory.objects.all(),
        to_field_name='id'
    )

    class Meta:
        model = UserNotification
        fields = ['status', 'notification_type', 'notification_category']
