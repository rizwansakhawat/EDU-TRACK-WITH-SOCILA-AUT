from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Enrollment


@receiver(post_save, sender=Enrollment)
def generate_certificate_on_completion(sender, instance, **kwargs):
    """Auto-generate a certificate when enrollment status becomes 'completed'."""
    if instance.status == "completed":
        from reports.models import Certificate

        Certificate.objects.get_or_create(enrollment=instance)
