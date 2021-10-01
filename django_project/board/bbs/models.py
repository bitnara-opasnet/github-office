from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class Post(models.Model):
    name = models.CharField(max_length=50)
    title = models.TextField()
    contents = models.TextField()
    # create_date = models.DateTimeField(default=timezone.now)
    create_date = models.DateTimeField(auto_now=True) # 데이터 수정시 현재시간으로 자동 저장

    def __str__(self):
        return self.title