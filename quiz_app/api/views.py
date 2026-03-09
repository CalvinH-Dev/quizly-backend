from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from quiz_app.api.permissions import IsQuizOwner
from quiz_app.api.serializers import (
    CreateQuizSerializer,
    QuizSerializer,
    UpdateQuizSerializer,
)
from quiz_app.models import Quiz


class QuizViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated & IsQuizOwner]
    serializer_class = QuizSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        if self.action == "list":
            return Quiz.objects.filter(owner=self.request.user)
        return Quiz.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateQuizSerializer
        if self.action == "partial_update":
            return UpdateQuizSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        url = request.data.get("url")
        # generate Quiz via Whisper AI + Gemini
        # quiz = Quiz.objects.create(owner=request.user, video_url=url, ...)

        # response_serializer = CreateQuizSerializer(quiz)
        # return Response(response_serializer.data, status=201)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdateQuizSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = QuizSerializer(instance)
        return Response(response_serializer.data)
