from django.db import models


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    loginname = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    group_id = models.CharField(max_length=255, blank=True, null=True)
    role = models.IntegerField()

    class Meta:
        db_table = 'user'


class Group(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    order = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'group'


class Holiday(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=255, blank=True, null=True)
    data = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'holiday'


class Scheduled(models.Model):
    group_id = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    day = models.CharField(max_length=255, blank=True, null=True)
    month = models.CharField(max_length=255, blank=True, null=True)
    week = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Scheduled'
