from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """Allow access only to the owner of a quiz."""

    def has_object_permission(self, request, view, obj) -> bool:
        """Return True if the requesting user is the quiz owner.

        Args:
            request: The incoming request.
            view: The view handling the request.
            obj: The quiz instance being accessed.
        """
        return request.user.id == obj.owner.id
