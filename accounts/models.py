from django.contrib.auth.models import AbstractUser
from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(AbstractUser):

    ROLE_CHOICES = (
        ("SUPERADMIN", "SuperAdmin"),
        ("ORGADMIN", "OrgAdmin"),
        ("INSTRUCTOR", "Instructor"),
        ("STUDENT", "Student"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )