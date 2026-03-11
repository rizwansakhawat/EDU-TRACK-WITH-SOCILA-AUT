from django.db import models

# Create your models here.
class Certificate(models.Model):
    enrollment = models.OneToOneField("enrollments.Enrollment", on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
