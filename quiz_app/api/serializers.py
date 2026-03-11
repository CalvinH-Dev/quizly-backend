from rest_framework import serializers

from quiz_app.models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize a question with its title and answer options."""

    question_title = serializers.SerializerMethodField()
    question_options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "question_title", "question_options", "answer"]

    def get_question_title(self, obj: Question) -> str:
        """Return the question's title."""
        return obj.title

    def get_question_options(self, obj: Question) -> list[str]:
        """Return a list of answer option texts for the question."""
        return list(obj.options.values_list("text", flat=True))


class CreateQuestionSerializer(QuestionSerializer):
    """Extend QuestionSerializer with timestamp fields for creation responses."""

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ["created_at", "updated_at"]


class QuizSerializer(serializers.ModelSerializer):
    """Serialize a quiz with its nested questions."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]


class CreateQuizSerializer(QuizSerializer):
    """Extend QuizSerializer with timestamped question data for creation responses."""

    questions = CreateQuestionSerializer(many=True, read_only=True)


class UpdateQuizSerializer(serializers.ModelSerializer):
    """Serialize only the editable fields of a quiz."""

    class Meta:
        model = Quiz
        fields = ["title", "description"]
