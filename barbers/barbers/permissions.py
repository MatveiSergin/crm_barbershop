from django.contrib.auth.models import Group
from rest_framework import permissions

def user_in_group(user, group_name):
    group = Group.objects.filter(name=group_name).first()
    if group is None:
        return False
    return group in user.groups.all()

class IsManager(permissions.BasePermission):
    group_name = "Manager"

    def has_permission(self, request, view):
        return user_in_group(request.user, self.group_name)

class IsManagerOrReadOnly(permissions.BasePermission):
    group_name = "Manager"
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return user_in_group(request.user, self.group_name)

class IsManagerOrIsOwner(permissions.BasePermission):
    group_name = "Manager"
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return False
        try:
            return request.user.staff == obj
        except AttributeError:
            return False

    def has_permission(self, request, view):
        if "pk" in request.parser_context['kwargs']:
            return True
        else:
            return user_in_group(request.user, self.group_name)
