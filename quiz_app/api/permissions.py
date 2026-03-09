from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """Permission class that allows access only to the owner of a profile."""

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user is the owner of the object."""
        user = request.user

        return user.id == obj.owner.id
