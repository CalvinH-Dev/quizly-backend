from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from quiz_app.api.permissions import IsQuizOwner


class QuizViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated & IsQuizOwner]

    def get_permissions(self):
        if self.action in ("create", "list"):
            return [IsAuthenticated]
        return super().get_permissions()
