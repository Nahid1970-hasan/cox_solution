"""
API root view for REST API - lists available endpoints.
"""
from django.http import JsonResponse
from django.shortcuts import redirect


def health(request):
    """GET /api/health/ - Health check (200 OK)."""
    return JsonResponse({"status": "ok"})


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
                "list_create": f"{base}/api/users/projects/",
                "detail": f"{base}/api/users/projects/<project_id>/",
            },
            "auth": {
                "login": f"{base}/api/users/login/",
                "logout": f"{base}/api/users/logout/",
            },
            "admin": f"{base}/admin/",
        },
    })
