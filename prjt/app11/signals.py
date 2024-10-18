from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerevalAdded


@receiver(post_save, sender=PerevalAdded)
def set_default_status(sender, instance, created, **kwargs):
    if created:
        instance.status = 'new'
        instance.save()