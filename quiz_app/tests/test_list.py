from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.test_helpers.auth_helpers import create_user
from quiz_app.tests.helpers import (
    assert_question_options,
    create_quiz_with_questions,
)


class QuizListTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.login_data = {"username": "testuser", "password": "testpass123"}
        self.user = create_user(**self.login_data, email="test@example.com")
        self.other_user = create_user(
            username="other", password="testpass123", email="other@example.com"
        )
        self._login()

    def _login(self):
        url = reverse("login")
        self.client.post(url, self.login_data, format="json")

    def test_list_ok(self):
        quiz1 = create_quiz_with_questions(
            owner=self.user,
            title="Quiz 1",
            description="Description 1",
            video_url="https://youtube.com/1",
        )
        quiz2 = create_quiz_with_questions(
            owner=self.user,
            title="Quiz 2",
            description="Description 2",
            video_url="https://youtube.com/2",
        )
        url = reverse("quiz-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        ids = [q["id"] for q in response.data]
        self.assertIn(quiz1.id, ids)
        self.assertIn(quiz2.id, ids)
        titles = [q["title"] for q in response.data]
        self.assertIn("Quiz 1", titles)
        self.assertIn("Quiz 2", titles)
        for quiz in response.data:
            self.assertEqual(len(quiz["questions"]), 2)
            for question in quiz["questions"]:
                assert_question_options(self, question)

    def test_list_only_own_quizzes(self):
        create_quiz_with_questions(
            owner=self.user, title="My Quiz", video_url="https://youtube.com/1"
        )
        create_quiz_with_questions(
            owner=self.other_user,
            title="Other Quiz",
            video_url="https://youtube.com/2",
        )
        url = reverse("quiz-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_unauthenticated(self):
        self.client.cookies.clear()
        url = reverse("quiz-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
