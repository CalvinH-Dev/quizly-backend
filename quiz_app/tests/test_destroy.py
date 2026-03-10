from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.test_helpers.auth_helpers import create_user
from quiz_app.models import Quiz
from quiz_app.tests.helpers import create_quiz_with_questions


class QuizDestroyTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.login_data = {"username": "testuser", "password": "testpass123"}
        self.user = create_user(**self.login_data, email="test@example.com")
        self.other_user = create_user(
            username="other", password="testpass123", email="other@example.com"
        )
        self.quiz = create_quiz_with_questions(
            owner=self.user, title="My Quiz", video_url="https://youtube.com/1"
        )
        self._login()

    def _login(self):
        url = reverse("login")
        self.client.post(url, self.login_data, format="json")

    def test_destroy_ok(self):
        url = reverse("quiz-detail", args=[self.quiz.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=self.quiz.id).exists())

    def test_destroy_not_found(self):
        url = reverse("quiz-detail", args=[99999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_other_user_quiz(self):
        other_quiz = create_quiz_with_questions(
            owner=self.other_user,
            title="Other Quiz",
            video_url="https://youtube.com/2",
        )
        url = reverse("quiz-detail", args=[other_quiz.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_unauthenticated(self):
        self.client.cookies.clear()
        url = reverse("quiz-detail", args=[self.quiz.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
