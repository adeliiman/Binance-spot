from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.http import JsonResponse, HttpRequest, HttpResponse
from django_filters.views import FilterView
import django_filters
import csv
from io import TextIOWrapper

from .models import Customer, CustomerGroup, SMSTemplate, SMSCampaign
from .tasks import render_template, send_sms


class DashboardView(LoginRequiredMixin, TemplateView):
	template_name = "dashboard.html"

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["customers_count"] = Customer.objects.count()
		ctx["groups_count"] = CustomerGroup.objects.count()
		ctx["campaigns_count"] = SMSCampaign.objects.count()
		return ctx


class CustomerFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(lookup_expr="icontains")
	mobile = django_filters.CharFilter(lookup_expr="icontains")
	group = django_filters.ModelChoiceFilter(queryset=CustomerGroup.objects.all(), required=False)

	class Meta:
		model = Customer
		fields = ["name", "mobile", "group"]


class CustomerListView(LoginRequiredMixin, FilterView):
	model = Customer
	template_name = "customers/list.html"
	paginate_by = 20
	filterset_class = CustomerFilter


class CustomerDetailView(LoginRequiredMixin, DetailView):
	model = Customer
	template_name = "customers/detail.html"


class CustomerCreateView(LoginRequiredMixin, CreateView):
	model = Customer
	fields = ["name", "mobile", "birth_date", "visit_count", "notes", "last_visit", "group"]
	success_url = reverse_lazy("customer_list")
	template_name = "customers/form.html"


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
	model = Customer
	fields = ["name", "mobile", "birth_date", "visit_count", "notes", "last_visit", "group"]
	success_url = reverse_lazy("customer_list")
	template_name = "customers/form.html"


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
	model = Customer
	success_url = reverse_lazy("customer_list")
	template_name = "confirm_delete.html"


class GroupListView(LoginRequiredMixin, ListView):
	model = CustomerGroup
	template_name = "groups/list.html"


class GroupDetailView(LoginRequiredMixin, DetailView):
	model = CustomerGroup
	template_name = "groups/detail.html"

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["object_list"] = CustomerGroup.objects.exclude(pk=self.object.pk)
		return ctx


def group_reassign_api(request: HttpRequest):
	if request.method != "POST":
		return JsonResponse({"error": "POST required"}, status=400)
	customer_id = request.POST.get("customer_id")
	group_id = request.POST.get("group_id")
	customer = get_object_or_404(Customer, pk=customer_id)
	group = get_object_or_404(CustomerGroup, pk=group_id)
	customer.group = group
	customer.save(update_fields=["group"])
	return JsonResponse({"ok": True})


class TemplateListView(LoginRequiredMixin, ListView):
	model = SMSTemplate
	template_name = "templates/list.html"


class TemplateCreateView(LoginRequiredMixin, CreateView):
	model = SMSTemplate
	fields = ["name", "content", "type", "active"]
	success_url = reverse_lazy("template_list")
	template_name = "templates/form.html"


class TemplateUpdateView(LoginRequiredMixin, UpdateView):
	model = SMSTemplate
	fields = ["name", "content", "type", "active"]
	success_url = reverse_lazy("template_list")
	template_name = "templates/form.html"


class TemplateDeleteView(LoginRequiredMixin, DeleteView):
	model = SMSTemplate
	success_url = reverse_lazy("template_list")
	template_name = "confirm_delete.html"


class CampaignListView(LoginRequiredMixin, ListView):
	model = SMSCampaign
	template_name = "campaigns/list.html"


class CampaignCreateView(LoginRequiredMixin, CreateView):
	model = SMSCampaign
	fields = ["title", "template", "recipients", "scheduled_for", "status"]
	success_url = reverse_lazy("campaign_list")
	template_name = "campaigns/form.html"


def campaign_preview(request: HttpRequest, pk: int):
	campaign = get_object_or_404(SMSCampaign, pk=pk)
	# Preview using first recipient
	first = campaign.recipients.first()
	context = {"name": first.name if first else "Customer", "mobile": first.mobile if first else ""}
	body = render_template(campaign.template.content, context)
	return render(request, "campaigns/preview.html", {"campaign": campaign, "body": body})


def campaign_send(request: HttpRequest, pk: int):
	campaign = get_object_or_404(SMSCampaign, pk=pk)
	for customer in campaign.recipients.all():
		body = render_template(campaign.template.content, {"name": customer.name, "mobile": customer.mobile})
		send_sms(customer.mobile, body)
	campaign.mark_sent()
	return redirect("campaign_list")


def customer_export(request: HttpRequest) -> HttpResponse:
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="customers.csv"'
	writer = csv.writer(response)
	writer.writerow(["name","mobile","birth_date","visit_count","notes","last_visit","group"])
	for c in Customer.objects.select_related("group").all():
		writer.writerow([
			c.name, c.mobile,
			c.birth_date.isoformat() if c.birth_date else "",
			c.visit_count,
			c.notes.replace('\n',' ') if c.notes else "",
			c.last_visit.isoformat() if c.last_visit else "",
			c.group.name if c.group else "",
		])
	return response


def customer_import(request: HttpRequest):
	if request.method == "POST" and request.FILES.get("file"):
		file = TextIOWrapper(request.FILES["file"].file, encoding="utf-8")
		reader = csv.DictReader(file)
		for row in reader:
			group = None
			group_name = (row.get("group") or "").strip()
			if group_name:
				group, _ = CustomerGroup.objects.get_or_create(name=group_name)
			cust, created = Customer.objects.update_or_create(
				mobile=row.get("mobile").strip(),
				defaults={
					"name": row.get("name").strip(),
					"birth_date": (row.get("birth_date") or None) or None,
					"visit_count": int(row.get("visit_count") or 0),
					"notes": row.get("notes") or "",
					"last_visit": (row.get("last_visit") or None) or None,
					"group": group,
				}
			)
		return redirect("customer_list")
	return render(request, "customers/import.html")
