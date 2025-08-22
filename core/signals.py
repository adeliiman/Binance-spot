from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Customer
from .tasks import send_welcome_message


@receiver(post_save, sender=Customer)
def on_customer_created(sender, instance: Customer, created: bool, **kwargs):
	if created:
		send_welcome_message.delay(instance.id)