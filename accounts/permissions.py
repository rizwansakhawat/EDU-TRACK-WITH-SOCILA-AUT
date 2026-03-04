from rest_framework.permissions import BasePermission


class BaseRolePermission(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in self.allowed_roles
        )


class IsSuperAdmin(BaseRolePermission):
    allowed_roles = ["SUPERADMIN"]


class IsOrgAdmin(BaseRolePermission):
    allowed_roles = ["ORGADMIN"]


class IsInstructor(BaseRolePermission):
    allowed_roles = ["INSTRUCTOR"]


class IsStudent(BaseRolePermission):
    allowed_roles = ["STUDENT"]