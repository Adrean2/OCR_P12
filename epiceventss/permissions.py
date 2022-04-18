from rest_framework.permissions import BasePermission, SAFE_METHODS
from datetime import datetime
from . import models

EDIT_METHODS = ("PUT", "PATCH")


def has_expired(obj):
    if obj.event_date < datetime.now():
        return True
    else:
        return False


class IsAdminAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return super().has_permission(self, request)


class IsGestion(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True

    def has_object_permission(self, request, view, obj):
        return True


class ContractPermission(BasePermission):
    message = "Vous ne pouvez pas supprimer de contrat"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        # Permissions si commercial
        if request.user.role == "C":
            if request.method in (SAFE_METHODS, "POST"):
                return True
            elif request.method in EDIT_METHODS:
                self.message = "Vous n'êtes pas le commercial référent"
                return obj.sales_contact == request.user
            else:
                return False

        # Permissions si support
        if request.user.role == "S":
            if request.method in SAFE_METHODS:
                return True
            else:
                self.message = "Vous ne pouvez pas modifier/créer de contracts."
                return False

        # Permission admin
        if request.user.is_superuser or request.user.role == "G":
            return True
        return False


class ClientPermission(BasePermission):
    message = "Vous ne pouvez pas supprimer de client"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):

        if request.user.role == "C":
            if request.method in (SAFE_METHODS, "POST"):
                return True
            elif request.method in EDIT_METHODS:
                self.message = "Vous n'êtes pas le commercial référent"
                return obj.sales_contact == request.user
        if request.user.role == "S":
            if request.method in SAFE_METHODS:
                return True
            else:
                self.message = "Vous ne pouvez pas modifier/créer de client."
                return False

        if request.user.is_superuser or request.user.role == "G":
            return True
        return False


class EventPermission(BasePermission):
    message = "Vous ne pouvez pas supprimer d'évènements"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.role == "C":
            if request.method in (SAFE_METHODS, "POST"):
                return True
            elif request.method in EDIT_METHODS:
                self.message = "Vous n'êtes pas le commercial référent"
                return obj.client.sales_contact == request.user

        if request.user.role == "S":
            if request.method in SAFE_METHODS:
                return True
            elif request.method in EDIT_METHODS:
                self.message = "Vous n'êtes pas le support référent"
                if not has_expired(obj):
                    return obj.support_contact == request.user
                else:
                    self.message = "L'évènement est terminé, vous ne pouvez plus le modifier."

        if request.user.is_superuser or request.user.role == "G":
            return True
        return False
