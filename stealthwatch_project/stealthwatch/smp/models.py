from os import name
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50)
    image = models.ImageField(blank=True)

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
        db_table = 'profile'

    def __str__(self):
        return self.user.username

class ApiConfig(models.Model):
    ipaddress = models.GenericIPAddressField(default='0.0.0.0')
    username = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.username

class TagList(models.Model):
    tagid = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'taglist'
        verbose_name_plural = 'taglists'
        db_table = 'taglist'

    def __str__(self):
        return "{}".format(self.tagid)