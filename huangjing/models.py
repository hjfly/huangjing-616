from django.db import models


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=255)
    loginname = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    group_id = models.CharField(max_length=255)
    role = models.IntegerField()

    class Meta:
        db_table = 'user'


class Group(models.Model):
    name = models.CharField(max_length=255)
    order = models.CharField(max_length=255)

    class Meta:
        db_table = 'group'


class Holiday(models.Model):
    name = models.CharField(max_length=255)
    year = models.CharField(max_length=255)
    data = models.CharField(max_length=255)

    class Meta:
        db_table = 'holiday'


class Scheduled(models.Model):
    group_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    day = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    week = models.CharField(max_length=255)
    year = models.CharField(max_length=255)

    class Meta:
        db_table = 'Scheduled'
