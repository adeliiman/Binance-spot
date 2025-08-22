from django.db import models
from django.utils import timezone


class CustomerGroup(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)

	def __str__(self) -> str:
		return self.name


class Customer(models.Model):
	name = models.CharField(max_length=255)
	mobile = models.CharField(max_length=20, unique=True)
	birth_date = models.DateField(null=True, blank=True)
	visit_count = models.PositiveIntegerField(default=0)
	notes = models.TextField(blank=True)
	last_visit = models.DateField(null=True, blank=True)
	group = models.ForeignKey(CustomerGroup, null=True, blank=True, on_delete=models.SET_NULL, related_name="customers")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"{self.name} ({self.mobile})"


class SMSTemplate(models.Model):
	WELCOME = "welcome"
	BIRTHDAY = "birthday"
	REMINDER = "reminder"
	CUSTOM = "custom"

	TEMPLATE_TYPES = [
		(WELCOME, "Welcome"),
		(BIRTHDAY, "Birthday"),
		(REMINDER, "Reminder"),
		(CUSTOM, "Custom"),
	]

	name = models.CharField(max_length=100, unique=True)
	content = models.TextField(help_text="Use placeholders like {{name}}, {{mobile}}, {{days}}")
	type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default=CUSTOM)
	active = models.BooleanField(default=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"{self.name} ({self.type})"


class SMSCampaign(models.Model):
	DRAFT = "draft"
	SCHEDULED = "scheduled"
	SENT = "sent"
	FAILED = "failed"

	STATUS_CHOICES = [
		(DRAFT, "Draft"),
		(SCHEDULED, "Scheduled"),
		(SENT, "Sent"),
		(FAILED, "Failed"),
	]

	title = models.CharField(max_length=150)
	recipients = models.ManyToManyField(Customer, related_name="campaigns")
	template = models.ForeignKey(SMSTemplate, on_delete=models.PROTECT, related_name="campaigns")
	scheduled_for = models.DateTimeField(null=True, blank=True)
	sent_date = models.DateTimeField(null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def mark_sent(self) -> None:
		self.status = self.SENT
		self.sent_date = timezone.now()
		self.save(update_fields=["status", "sent_date"])
