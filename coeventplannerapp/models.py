from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Add any additional fields you want to include in your custom user model
    

    def __str__(self):
        return self.username