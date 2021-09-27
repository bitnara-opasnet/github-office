from django.db import models
import datetime

# Create your models here.
class Post(models.Model):
    name = models.CharField(max_length=50)
    title = models.TextField()
    contents = models.TextField()
    create_date = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.title