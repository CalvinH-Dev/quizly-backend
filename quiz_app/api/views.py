from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from quiz_app.api.permissions import IsQuizOwner
from quiz_app.api.serializers import (
    CreateQuizSerializer,
    QuizSerializer,
    UpdateQuizSerializer,
)
from quiz_app.api.services import (
    fetch_transcript,
    generate_quiz_from_json_transcript,
)
from quiz_app.api.utils import save_quiz
from quiz_app.models import Quiz


class QuizViewSet(ModelViewSet):
    """ViewSet for creating, retrieving, updating, and deleting quizzes."""

    permission_classes = [IsAuthenticated & IsQuizOwner]
    serializer_class = QuizSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        """Return all quizzes for detail actions, or only the user's own quizzes for list."""
        if self.action == "list":
            return Quiz.objects.filter(owner=self.request.user)
        return Quiz.objects.all()

    def get_permissions(self):
        """Allow authenticated users to create; enforce ownership for all other actions."""
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Return the appropriate serializer based on the current action."""
        if self.action == "create":
            return CreateQuizSerializer
        if self.action == "partial_update":
            return UpdateQuizSerializer
        return super().get_serializer_class()

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Generate a quiz from a YouTube URL and persist it.

        Args:
            request: Incoming request containing the YouTube video URL.

        Returns:
            201 with the created quiz data, or 400 if generation fails.
        """
        url = request.data.get("url")
        try:
            transcript_json = fetch_transcript(url)
            quiz_json = generate_quiz_from_json_transcript(transcript_json)
            quiz = save_quiz(quiz_json, url, request.user)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        return Response(CreateQuizSerializer(quiz).data, status=201)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """Partially update a quiz's fields and return the full updated representation.

        Args:
            request: Incoming request containing the fields to update.

        Returns:
            200 with the full updated quiz data.
        """
        instance = self.get_object()
        serializer = UpdateQuizSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(QuizSerializer(instance).data)
