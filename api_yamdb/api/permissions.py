from rest_framework import permissions


class YaMDB_Admin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_staff is True
