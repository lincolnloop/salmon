from rest_framework import permissions

class SalmonPermission(permissions.IsAdminUser):
    """
    Check for the token the SettingsAuthenicator sets on the request
    or if the user is an admin
    """

    def has_permission(self, request, view):
        if getattr(request, '_salmon_allowed', False):
            return True
        return super(SalmonPermission, self).has_permission(request, view)
