from django.db import models

# Create your models here.
class Enrollment(models.Model):
    student = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20, choices=[
            ("active", "Active"),
            ("completed", "Completed"),
            ("dropped", "Dropped") ], default="active" )

    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course"  )]

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"
    
