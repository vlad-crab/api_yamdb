from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission
from reviews.models import Review, Comment


class CustomPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET' or request.get("user").role == 'admin':
            return True
        elif request.get("user").role == 'moderator' and type(obj) in (Comment, Review):
            return True
        elif request.get("user").role == 'user':
            if request.method == 'POST':
                return True
            elif type(obj) in (Comment, Review):
                if request.user == obj.author:
                    return True
        return False
