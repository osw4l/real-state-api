from rest_framework.permissions import BasePermission


class IsCompanyUser(BasePermission):
    """
    Allows access only to company users.
    """

    def has_permission(self, request, view):
        return hasattr(request.user, 'companyuser')

