"""
Fixed local allowlist (defence in depth — the server enforces its own registry too).
There is deliberately no shell, file-system or generic HTTP tool.
"""
import json

SERVER_TOOLS = {
    # read
    "get_my_profile", "search_my_projects", "get_cv_versions", "get_job_preferences", "search_jobs", "get_job_details",
    "get_application", "get_pending_approvals", "get_agent_status", "get_activity_history", "list_job_accounts",
    "get_job_account_status", "get_job_account_capabilities", "get_job_account_permissions", "test_job_account_connection",
    "search_jobs_from_connected_sources",
    # prepare
    "analyze_job_match", "prepare_application", "prepare_job_application",
    # write
    "add_job", "create_application_draft", "request_application_approval", "record_application_result",
    "request_job_account_connection", "request_job_account_permission",
    # external (server requires a consumed approval)
    "submit_application",
    # critical (server only creates an approval request)
    "disconnect_job_account", "revoke_job_account_access",
}
LOCAL_TOOLS = {"open_application_page"}
QUEUED_TASK_FORBIDDEN = {"submit_application", "disconnect_job_account", "revoke_job_account_access"}
MAX_PAYLOAD = 64 * 1024


class TaskRejected(Exception):
    pass


def validate_task(task):
    """Validate a task received from the server before doing anything."""
    if not isinstance(task, dict):
        raise TaskRejected("task_not_an_object")
    tool, payload = task.get("tool"), task.get("payload", {})
    if tool not in SERVER_TOOLS | LOCAL_TOOLS:
        raise TaskRejected(f"tool_not_allowlisted:{tool}")
    if tool in QUEUED_TASK_FORBIDDEN:
        raise TaskRejected("external_or_critical_tools_cannot_be_queued")
    if not isinstance(payload, dict):
        raise TaskRejected("payload_not_an_object")
    if len(json.dumps(payload)) > MAX_PAYLOAD:
        raise TaskRejected("payload_too_large")
    return tool, payload
