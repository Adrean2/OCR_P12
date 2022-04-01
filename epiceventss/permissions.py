from rest_framework.permissions import BasePermission, SAFE_METHODS
from . import models


class isAdminAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return super().has_permission(request, view)


class isGestion(BasePermission):
    def has_object_permission(self, request, view, obj):
        return True


class isSupport(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.support_contact


class isSales(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.sales_contact
