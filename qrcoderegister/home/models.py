from django.db import models
from django.contrib.auth.models import User

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(max_length=45, null=True, blank=True)
    random_code = models.CharField(max_length=5,null=True, blank=True)


    class Meta:
        unique_together = ['user', 'timestamp',]
