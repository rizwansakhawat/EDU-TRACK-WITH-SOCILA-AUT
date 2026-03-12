from django.db import models
    
class Payment(models.Model):

    enrollment = models.ForeignKey("enrollments.Enrollment", on_delete=models.CASCADE, related_name="payments" )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent = models.CharField(  max_length=255,  null=True,  blank=True)
    status = models.CharField( max_length=20,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed")], default="pending" )
    paid_at = models.DateTimeField(null=True, blank=True )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.enrollment.student} - {self.enrollment.course}"
# Create your models here.
