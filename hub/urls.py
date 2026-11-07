from django.urls import path

from . import api, views

app_name = "hub"

urlpatterns = [
    path("login/", views.hub_login, name="login"),
    path("login/verify/", views.hub_mfa, name="mfa"),
    path("logout/", views.hub_logout, name="logout"),

    path("", views.overview, name="overview"),
    path("guide/", views.guide, name="guide"),
    path("profile/", views.profile, name="profile"),
    path("profile/<int:pk>/", views.profile, name="fact_edit"),
    path("profile/<int:pk>/delete/", views.fact_delete, name="fact_delete"),
    path("documents/", views.documents, name="documents"),
    path("documents/<int:pk>/", views.documents, name="document_edit"),
    path("documents/<int:pk>/download/", views.document_download, name="document_download"),
    path("documents/<int:pk>/toggle/", views.document_toggle, name="document_toggle"),

    path("jobs/", views.jobs, name="jobs"),
    path("jobs/preferences/", views.preferences, name="preferences"),
    path("jobs/<int:pk>/", views.job_detail, name="job"),
    path("jobs/<int:pk>/prepare/", views.job_prepare, name="job_prepare"),
    path("jobs/<int:pk>/archive/", views.job_archive, name="job_archive"),
    path("jobs/sync/<int:account_pk>/", views.jobs_sync, name="jobs_sync"),
    path("applications/", views.applications, name="applications"),
    path("applications/export.csv", views.applications_csv, name="applications_csv"),
    path("applications/<int:pk>/", views.application_detail, name="application"),

    path("accounts/", views.integrations, name="integrations"),
    path("accounts/oauth/<slug:slug>/start/", views.oauth_start, name="oauth_start"),
    path("accounts/oauth/<slug:key>/callback/", views.oauth_callback, name="oauth_callback"),
    path("accounts/jobs/", views.job_accounts, name="job_accounts"),
    path("accounts/jobs/add/", views.job_account_add, name="job_account_add"),
    path("accounts/jobs/add/<slug:slug>/", views.job_account_add, name="job_account_add_provider"),
    path("accounts/jobs/emergency-stop/", views.job_accounts_emergency, name="job_accounts_emergency"),
    path("accounts/<int:pk>/", views.account_detail, name="account"),

    path("agent/", views.agent, name="agent"),
    path("agent/devices/register/", views.device_register, name="device_register"),
    path("agent/devices/<int:pk>/", views.device_action, name="device_action"),
    path("agent/devices/<int:pk>/tools/", views.device_tools, name="device_tools"),
    path("agent/tasks/<uuid:pk>/", views.task_detail, name="task"),
    path("approvals/", views.approvals, name="approvals"),
    path("approvals/<uuid:pk>/", views.approval_detail, name="approval"),
    path("activity/", views.activity, name="activity"),
    path("content/", views.content, name="content"),
    path("security/", views.security, name="security"),

    # Agent API (bearer tokens, outbound from the local agent)
    path("api/agent/token/", api.token, name="api_token"),
    path("api/agent/heartbeat/", api.heartbeat, name="api_heartbeat"),
    path("api/agent/tools/", api.tool_list, name="api_tools"),
    path("api/agent/tools/<slug:name>/", api.tool_call, name="api_tool_call"),
    path("api/agent/tasks/next/", api.next_task, name="api_next_task"),
    path("api/agent/tasks/<uuid:task_id>/progress/", api.task_progress, name="api_task_progress"),
    path("api/agent/tasks/<uuid:task_id>/complete/", api.task_complete, name="api_task_complete"),
    path("api/agent/cv/<int:pk>/download/", api.cv_download, name="api_cv_download"),
]
