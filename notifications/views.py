from django.db.models import Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView, ListCreateAPIView, CreateAPIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from .filters import NotificationFilterBackend
from .models import UserNotification, TranslationString, UserNotificationSettings, UserNotificationOption, User
from .serializers import (
    UserNotificationSerializer,
    UserNotificationSettingsSerializer,
    UserNotificationStatusSerializer
)


class ListCreateNotificationView(ListCreateAPIView):
    serializer_class = UserNotificationSerializer
    http_method_names = ["post", "get"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NotificationFilterBackend

    def perform_create(self, serializer):
        user_id = self.kwargs.get("user_id")
        serializer.save(user_id=user_id)


    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)

        translations_prefetch = Prefetch(
            "notification_template__translations",
            queryset=TranslationString.objects.filter(language=user.language),
            to_attr="prefetched_translations",
        )

        options_prefetch = Prefetch(
            'options',
            queryset=UserNotificationOption.objects.all(),
            to_attr='prefetched_options'
        )

        restricted_system_templates = UserNotificationSettings.objects.filter(
            user_id=user_id,
            system_notification=0
        ).values_list("notification_template_id", flat=True)

        restricted_push_templates = UserNotificationSettings.objects.filter(
            user_id=user_id,
            push_notification=0
        ).values_list("notification_template_id", flat=True)

        return (
            UserNotification.objects.filter(user_id=user_id, status=0)
            .select_related("notification_template", "notification_template__notification_category")
            .exclude(
                Q(notification_type=1, notification_template__id__in=restricted_system_templates) |
                Q(notification_type=2, notification_template__id__in=restricted_push_templates)
            )
            .prefetch_related(
                translations_prefetch,
                options_prefetch
            )
        )


class UpdateNotificationStatusView(UpdateAPIView):
    serializer_class = UserNotificationStatusSerializer
    http_method_names = ["put"]

    def get_object(self):
        user_id = self.kwargs.get("user_id")
        notification_id = self.kwargs.get("notification_id")

        return get_object_or_404(UserNotification, user_id=user_id, id=notification_id)

    def partial_update(self, request, *args, **kwargs):
        if "status" not in request.data:
            raise ValidationError({"status": "This field is required."})
        return super().partial_update(request, *args, **kwargs)


class UpdateNotificationSettingsView(CreateAPIView):
    serializer_class = UserNotificationSettingsSerializer

    def post(self, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get("user_id"))

        notification_template_id = self.request.data.get("notification_template")
        system_notification = self.request.data.get("system_notification")
        push_notification = self.request.data.get("push_notification")

        if not all((notification_template_id, system_notification, push_notification)):
            return Response(
                {"error": "Fields 'notification_template', 'system_notification', and 'push_notification' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification_settings, created = UserNotificationSettings.objects.update_or_create(
            user=user,
            notification_template_id=notification_template_id,
            defaults={
                "system_notification": system_notification,
                "push_notification": push_notification,
            },
        )

        response_data = {
            "id": notification_settings.id,
            "user": notification_settings.user.id,
            "notification_template_id": notification_settings.notification_template_id,
            "system_notification": notification_settings.system_notification,
            "push_notification": notification_settings.push_notification,
            "created": created,
        }

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(response_data, status=status_code)
