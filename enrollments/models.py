from django.db import models

# Create your models here.
class Enrollment(models.Model):
    student = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    course = models.ForeignKey( "courses.Course",  on_delete=models.CASCADE  )
    is_completed = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course" ) ]

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class Payment(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)