from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.test_helpers.auth_helpers import create_user
from quiz_app.models import Quiz
from quiz_app.tests.helpers import assert_question_options

VALID_QUIZ_DATA = {
    "title": "Test Quiz",
    "description": "Test Description",
    "questions": [
        {
            "question_title": f"Question {i}",
            "question_options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ],
            "answer": "Option A",
        }
        for i in range(1, 11)
    ],
}


class QuizCreateTest(APITestCase):
    def setUp(self):
        super().setUp()
        self.login_data = {"username": "testuser", "password": "testpass123"}
        self.user = create_user(**self.login_data, email="test@example.com")
        self.url = reverse("quiz-list")
        self._login()

    def _login(self):
        url = reverse("login")
        self.client.post(url, self.login_data, format="json")

    @patch("quiz_app.api.views.fetch_transcript")
    @patch("quiz_app.api.views.generate_quiz_from_json_transcript")
    def test_create_ok(self, mock_generate, mock_fetch):
        mock_fetch.return_value = "transcript"
        mock_generate.return_value = VALID_QUIZ_DATA

        response = self.client.post(
            self.url, {"url": "https://youtu.be/dQw4w9WgXcQ"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], VALID_QUIZ_DATA["title"])
        self.assertEqual(
            response.data["description"], VALID_QUIZ_DATA["description"]
        )
        self.assertEqual(
            response.data["video_url"], "https://youtu.be/dQw4w9WgXcQ"
        )
        self.assertEqual(len(response.data["questions"]), 10)
        for question in response.data["questions"]:
            assert_question_options(self, question)
        self.assertTrue(Quiz.objects.filter(owner=self.user).exists())

    @patch("quiz_app.api.views.fetch_transcript")
    @patch("quiz_app.api.views.generate_quiz_from_json_transcript")
    def test_create_invalid_url(self, mock_generate, mock_fetch):
        mock_fetch.side_effect = ValueError("Invalid or missing YouTube URL.")

        response = self.client.post(
            self.url, {"url": "https://notyoutube.com/watch"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Quiz.objects.filter(owner=self.user).exists())

    @patch("quiz_app.api.views.fetch_transcript")
    @patch("quiz_app.api.views.generate_quiz_from_json_transcript")
    def test_create_transcript_error(self, mock_generate, mock_fetch):
        mock_fetch.side_effect = Exception(
            "Transcript could not be generated."
        )

        response = self.client.post(
            self.url, {"url": "https://youtu.be/dQw4w9WgXcQ"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Quiz.objects.filter(owner=self.user).exists())

    @patch("quiz_app.api.views.fetch_transcript")
    @patch("quiz_app.api.views.generate_quiz_from_json_transcript")
    def test_create_invalid_quiz_data(self, mock_generate, mock_fetch):
        mock_fetch.return_value = "transcript"
        mock_generate.return_value = {
            **VALID_QUIZ_DATA,
            "questions": VALID_QUIZ_DATA["questions"][:5],
        }

        response = self.client.post(
            self.url, {"url": "https://youtu.be/dQw4w9WgXcQ"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Quiz.objects.filter(owner=self.user).exists())

    @patch("quiz_app.api.views.fetch_transcript")
    @patch("quiz_app.api.views.generate_quiz_from_json_transcript")
    def test_create_missing_url(self, mock_generate, mock_fetch):
        mock_fetch.side_effect = ValueError("Invalid or missing YouTube URL.")

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Quiz.objects.filter(owner=self.user).exists())

    def test_create_unauthenticated(self):
        self.client.cookies.clear()
        response = self.client.post(
            self.url, {"url": "https://youtu.be/dQw4w9WgXcQ"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
