from django.urls import path
from . import views

urlpatterns = [
	path("", views.DashboardView.as_view(), name="dashboard"),

	# Customers
	path("customers/", views.CustomerListView.as_view(), name="customer_list"),
	path("customers/create/", views.CustomerCreateView.as_view(), name="customer_create"),
	path("customers/<int:pk>/", views.CustomerDetailView.as_view(), name="customer_detail"),
	path("customers/<int:pk>/edit/", views.CustomerUpdateView.as_view(), name="customer_edit"),
	path("customers/<int:pk>/delete/", views.CustomerDeleteView.as_view(), name="customer_delete"),
	path("customers/export/", views.customer_export, name="customer_export"),
	path("customers/import/", views.customer_import, name="customer_import"),

	# Groups
	path("groups/", views.GroupListView.as_view(), name="group_list"),
	path("groups/<int:pk>/", views.GroupDetailView.as_view(), name="group_detail"),
	path("groups/reassign/", views.group_reassign_api, name="group_reassign_api"),

	# SMS Templates
	path("templates/", views.TemplateListView.as_view(), name="template_list"),
	path("templates/create/", views.TemplateCreateView.as_view(), name="template_create"),
	path("templates/<int:pk>/edit/", views.TemplateUpdateView.as_view(), name="template_edit"),
	path("templates/<int:pk>/delete/", views.TemplateDeleteView.as_view(), name="template_delete"),

	# Campaigns
	path("campaigns/", views.CampaignListView.as_view(), name="campaign_list"),
	path("campaigns/create/", views.CampaignCreateView.as_view(), name="campaign_create"),
	path("campaigns/<int:pk>/preview/", views.campaign_preview, name="campaign_preview"),
	path("campaigns/<int:pk>/send/", views.campaign_send, name="campaign_send"),
]