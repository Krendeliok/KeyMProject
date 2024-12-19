from django.urls import path
from . import views

urlpatterns = [
    path(
        'users/<int:user_id>/notifications/',
        views.ListCreateNotificationView.as_view(),
        name='get_all-create-notification'
    ),
    path(
        "users/<int:user_id>/notifications/<int:notification_id>/status/",
         views.UpdateNotificationStatusView.as_view(),
         name="update-notification-status"
    ),
    path(
        "users/<int:user_id>/notification-settings/",
        views.UpdateNotificationSettingsView.as_view(),
        name="update-notification-settings",
    ),
]
