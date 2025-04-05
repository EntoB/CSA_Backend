from django.db import models
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.AutoField(primary_key=True,auto_created=True)
    phone_number = models.CharField(max_length=15,null=True,blank=True)
    #the name should be phone number staying as CharField validate in frontend with RegEx
    role = models.CharField(max_length=20, choices=[('superadmin', 'SuperAdmin'), ('admin', 'Admin'), ('customer', 'Customer')])

class RegistrationKey(models.Model):
    key = models.CharField(max_length=20, unique=True)
    for_role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('customer', 'Customer')])
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() < self.created_at + timedelta(days=1)
