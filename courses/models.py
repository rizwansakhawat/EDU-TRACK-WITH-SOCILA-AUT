from django.db import models

# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    institute = models.ForeignKey(
        "core.Institute",
        on_delete=models.CASCADE
    )
    instructor = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


class Module(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules"
    )


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons"
    )