from django.contrib import admin
from .models import Customer, CustomerGroup, SMSTemplate, SMSCampaign


@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
	list_display = ("name", "description")
	search_fields = ("name",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ("name", "mobile", "group", "visit_count", "last_visit")
	list_filter = ("group",)
	search_fields = ("name", "mobile")


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
	list_display = ("name", "type", "active", "updated_at")
	list_filter = ("type", "active")
	search_fields = ("name", "content")


@admin.register(SMSCampaign)
class SMSCampaignAdmin(admin.ModelAdmin):
	list_display = ("title", "template", "status", "scheduled_for", "sent_date")
	list_filter = ("status",)
	search_fields = ("title",)
