from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Quiz(models.Model):
    """Represent a quiz generated from a YouTube video."""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quizzes"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    video_url = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Quizzes"


class Question(models.Model):
    """Represent a single question belonging to a quiz."""

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions"
    )
    title = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        """Validate that the question has exactly 4 options.

        Raises:
            ValidationError: If the option count is not exactly 4.
        """
        super().clean()
        if self.pk:
            option_count = self.options.count()
            if option_count != 4:
                raise ValidationError(
                    f"A question must have exactly 4 options, but has {option_count}."
                )


class Option(models.Model):
    """Represent one of four answer options for a question."""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=255)

    def clean(self) -> None:
        """Validate that the question does not exceed 4 options.

        Raises:
            ValidationError: If the question already has 4 options.
        """
        super().clean()
        if not self.pk:
            if self.question.options.count() >= 4:
                raise ValidationError("A question can have at most 4 options.")

    def save(self, *args, **kwargs) -> None:
        """Run full validation before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
