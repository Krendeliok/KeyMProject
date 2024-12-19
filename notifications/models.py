from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Language(models.Model):
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)

    class Meta:
        db_table = "language"


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=45)
    role_id = models.SmallIntegerField()
    active = models.SmallIntegerField(default=0)
    verified = models.SmallIntegerField()
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING, default=1)
    last_login = None

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "user"


FIELD_CHOICES = [
    ("name", 1),
    ("title", 2),
    ("description", 3),
    ("text", 4),
    ("question", 5),
    ("answer", 6),
    ("additional", 7),
]


class TranslationString(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.IntegerField()
    related_item = GenericForeignKey("content_type", "object_id")
    translation_field_id = models.IntegerField(
        choices=FIELD_CHOICES,
        default=1,
    )
    language = models.ForeignKey(Language, on_delete=models.DO_NOTHING)
    text = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = ("content_type", "object_id", "translation_field_id", "language")
        db_table = "translation_string"



class Country(models.Model):
    name = models.CharField(max_length=25)
    code = models.CharField(max_length=5)
    code_exp = models.CharField(max_length=5)

    class Meta:
        db_table = "country"


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=510)
    address = models.CharField(max_length=510)
    started = models.DateTimeField(auto_now_add=True)
    lat = models.FloatField(default=0)
    ing = models.FloatField(default=0)
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE)
    archived = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "project"


class NotificationCategory(models.Model):
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "notification_category"


class NotificationTemplate(models.Model):
    notification_category = models.ForeignKey("NotificationCategory", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    txt = models.CharField(max_length=255)
    translations = GenericRelation(TranslationString)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "notification_template"


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    notification_type = models.SmallIntegerField()
    status = models.SmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_notification"


class UserNotificationOption(models.Model):
    user_notification = models.ForeignKey(UserNotification, related_name='options', on_delete=models.CASCADE)
    field_id = models.SmallIntegerField()
    txt = models.CharField(max_length=32)

    class Meta:
        db_table = "user_notification_option"


class UserNotificationSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_template = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE)
    system_notification = models.SmallIntegerField(default=0)
    push_notification = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "user_notification_setting"
