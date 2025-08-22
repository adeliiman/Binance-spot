from datetime import date, timedelta
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from twilio.rest import Client

from .models import Customer, SMSTemplate


def render_template(content: str, context: dict) -> str:
	message = content
	for key, value in context.items():
		message = message.replace(f"{{{{{key}}}}}", str(value))
	return message


def send_sms(to_number: str, body: str) -> None:
	if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER):
		raise RuntimeError("Twilio is not configured. Set TWILIO_* env vars.")
	client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
	client.messages.create(to=to_number, from_=settings.TWILIO_FROM_NUMBER, body=body)


@shared_task
def send_welcome_message(customer_id: int) -> None:
	try:
		customer = Customer.objects.get(id=customer_id)
		template = SMSTemplate.objects.filter(type=SMSTemplate.WELCOME, active=True).first()
		if not template:
			return
		body = render_template(template.content, {"name": customer.name, "mobile": customer.mobile})
		send_sms(customer.mobile, body)
	except Customer.DoesNotExist:
		return


@shared_task
def send_birthday_messages() -> int:
	today = date.today()
	customers = Customer.objects.filter(birth_date__month=today.month, birth_date__day=today.day)
	template = SMSTemplate.objects.filter(type=SMSTemplate.BIRTHDAY, active=True).first()
	if not template:
		return 0
	count = 0
	for c in customers:
		body = render_template(template.content, {"name": c.name, "mobile": c.mobile})
		send_sms(c.mobile, body)
		count += 1
	return count


@shared_task
def send_reminder_messages() -> int:
	template = SMSTemplate.objects.filter(type=SMSTemplate.REMINDER, active=True).first()
	if not template:
		return 0
	now = timezone.now().date()
	count = 0
	for days in (20, 50):
		cutoff = now - timedelta(days=days)
		customers = Customer.objects.filter(last_visit=cutoff)
		for c in customers:
			body = render_template(template.content, {"name": c.name, "mobile": c.mobile, "days": days})
			send_sms(c.mobile, body)
			count += 1
	return count