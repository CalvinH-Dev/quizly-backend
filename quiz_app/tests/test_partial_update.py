from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.test_helpers.auth_helpers import create_user
from quiz_app.tests.helpers import (
    assert_question_options,
    create_quiz_with_questions,
)


class QuizPartialUpdateTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.login_data = {"username": "testuser", "password": "testpass123"}
        self.user = create_user(**self.login_data, email="test@example.com")
        self.other_user = create_user(
            username="other", password="testpass123", email="other@example.com"
        )
        self.quiz = create_quiz_with_questions(
            owner=self.user,
            title="Old Title",
            video_url="https://youtube.com/1",
        )
        self._login()

    def _login(self):
        url = reverse("login")
        self.client.post(url, self.login_data, format="json")

    def test_partial_update_ok(self):
        url = reverse("quiz-detail", args=[self.quiz.id])
        response = self.client.patch(
            url, {"title": "New Title"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.quiz.id)
        self.assertEqual(response.data["title"], "New Title")
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, "New Title")
        self.assertEqual(len(response.data["questions"]), 2)
        for question in response.data["questions"]:
            assert_question_options(self, question)

    def test_partial_update_description(self):
        url = reverse("quiz-detail", args=[self.quiz.id])
        response = self.client.patch(
            url, {"description": "New Description"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.quiz.id)
        self.assertEqual(response.data["description"], "New Description")
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.description, "New Description")
        self.assertEqual(len(response.data["questions"]), 2)
        for question in response.data["questions"]:
            assert_question_options(self, question)

    def test_partial_update_not_found(self):
        url = reverse("quiz-detail", args=[99999])
        response = self.client.patch(
            url, {"title": "New Title"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_other_user_quiz(self):
        other_quiz = create_quiz_with_questions(
            owner=self.other_user,
            title="Other Quiz",
            video_url="https://youtube.com/2",
        )
        url = reverse("quiz-detail", args=[other_quiz.id])
        response = self.client.patch(url, {"title": "Hacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_unauthenticated(self):
        self.client.cookies.clear()
        url = reverse("quiz-detail", args=[self.quiz.id])
        response = self.client.patch(
            url, {"title": "New Title"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
