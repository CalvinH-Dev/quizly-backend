from rest_framework import serializers

from quiz_app.models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    question_title = serializers.SerializerMethodField()
    question_options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "question_title", "question_options", "answer"]

    def get_question_title(self, obj):
        return obj.title

    def get_question_options(self, obj):
        return list(obj.options.values_list("text", flat=True))


class CreateQuestionSerializer(QuestionSerializer):
    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ["created_at", "updated_at"]


class QuizSerializer(serializers.ModelSerializer):
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
    questions = CreateQuestionSerializer(many=True, read_only=True)


class UpdateQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["title", "description"]
