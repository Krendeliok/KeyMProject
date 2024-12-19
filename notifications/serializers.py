from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from .models import UserNotification, UserNotificationOption, UserNotificationSettings, NotificationTemplate


class NotificationTemplateDashboardSerializer(serializers.ModelSerializer):
    notification_category = serializers.SlugRelatedField(slug_field="title", read_only=True)
    class Meta:
        model = NotificationTemplate
        fields = "__all__"

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if hasattr(obj, 'prefetched_translations') and obj.prefetched_translations:
            data["txt"] = obj.prefetched_translations[0].text
        else:
            data["txt"] = obj.txt
        return data


class UserNotificationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationOption
        fields = ["field_id", "txt"]


class UserNotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    notification_template = NotificationTemplateDashboardSerializer(read_only=True)
    notification_template_id = serializers.PrimaryKeyRelatedField(
        queryset=NotificationTemplate.objects.all(),
        source='notification_template',
        write_only=True,
        label="Notification template"
    )
    status = serializers.IntegerField(read_only=True)
    txt = serializers.CharField(read_only=True)
    options = UserNotificationOptionSerializer(many=True, write_only=True)

    class Meta:
        model = UserNotification
        fields = ["id", "user", "notification_template", "notification_template_id", "txt", "notification_type", "status", "options"]

    def to_representation(self, obj):
        data = super().to_representation(obj)
        text = data["notification_template"]["txt"]
        if hasattr(obj, 'prefetched_options') and obj.prefetched_options:
            data["txt"] = text.format("", *[option.txt for option in obj.prefetched_options])
        else:
            data["txt"] = text
        return data

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])
        user_notification = UserNotification.objects.create(**validated_data)

        for option in options_data:
            UserNotificationOption.objects.create(user_notification=user_notification, **option)

        return user_notification


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = UserNotificationSettings
        fields = ["id", "user", "notification_template", "system_notification", "push_notification"]


class UserNotificationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ["status"]