"""
API root view for REST API - lists available endpoints.
"""
from django.http import JsonResponse
from django.shortcuts import redirect


def health(request):
    """GET /api/health/ - Health check (200 OK)."""
    return JsonResponse({"status": "ok"})


# Status options for Project and Blog (Incoming, Ongoing, Completed)
STATUS_OPTIONS = [
    {"value": "incoming", "label": "Incoming"},
    {"value": "ongoing", "label": "Ongoing"},
    {"value": "completed", "label": "Completed"},
]


def status_options(request):
    """GET /api/status_options/ - Returns status options for project/blog dropdowns."""
    return JsonResponse({"status_options": STATUS_OPTIONS})


def root_redirect(request):
    """GET / - Redirect to /api/."""
    return redirect("/api/")


def api_root(request):
    """GET /api/ - JSON listing of REST API endpoints."""
    base = request.build_absolute_uri("/").rstrip("/")
    return JsonResponse({
        "message": "REST API",
        "docs": f"{base}/api/",
        "health": f"{base}/api/health/",
        "endpoints": {
            "users": {
                "dashboarduser": f"{base}/api/dashboarduser/",
                "alluser": f"{base}/api/alluser/",
                "alluser_detail": f"{base}/api/alluser/<id>/",
                "addusers": f"{base}/api/addusers/",
                "updateusers": f"{base}/api/updateusers/<id>/",
                "update_role": f"{base}/api/updateusers/<id>/role/",
                "deleteusers": f"{base}/api/deleteusers/<id>/",
            },
            "superadmin": {
                "superadmin_dashboard": f"{base}/api/superadmin_dashboard/",
                "alladminuser": f"{base}/api/alladminuser/<id>/",
                "add_admin_users": f"{base}/api/add_admin_users/",
                "update_admin_users": f"{base}/api/update_admin_users/<id>/",
                "delete_admin_users": f"{base}/api/delete_admin_users/<id>/",
            },
            "owners": {
                "list_create": f"{base}/api/users/owners/",
                "detail": f"{base}/api/users/owners/<owner_id>/",
            },
            "projects": {
                "projectdashboard": f"{base}/api/projectdashboard/",
                "project_public_dashboard": f"{base}/api/project_public_dashboard/",
                "projectall": f"{base}/api/projectall/<project_id>/",
                "add_project": f"{base}/api/add_project/",
                "update_project": f"{base}/api/update_project/<project_id>/",
                "delete_project": f"{base}/api/delete_project/<project_id>/",
            },
            "blog": {
                "blogdashboard": f"{base}/api/blogdashboard/",
                "blogall": f"{base}/api/blogall/<blog_id>/",
                "add_blog": f"{base}/api/add_blog/",
                "update_blog": f"{base}/api/update_blog/<blog_id>/",
                "delete_blog": f"{base}/api/delete_blog/<blog_id>/",
            },
            "status_options": f"{base}/api/status_options/",
            "contact": {
                "list_create": f"{base}/api/contacts/",
                "save": f"{base}/api/save_contacts/",
                "delete": f"{base}/api/delete_contacts/<contact_id>/",
            },
            "uploads": {
                "upload_file": f"{base}/api/upload/",
            },
            "auth": {
                "login": f"{base}/api/users/login/",
                "logout": f"{base}/api/users/logout/",
            },
            "admin": f"{base}/admin/",
        },
    })
