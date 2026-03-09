from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.test_helpers.auth_helpers import create_user
from quiz_app.models import Option, Question, Quiz


def create_quiz(owner, **kwargs):
    return Quiz.objects.create(owner=owner, **kwargs)


def create_question(quiz, **kwargs):
    return Question.objects.create(quiz=quiz, **kwargs)


def create_option(question, **kwargs):
    return Option.objects.create(question=question, **kwargs)


def create_question_with_options(quiz, title, answer):
    question = create_question(quiz=quiz, title=title, answer=answer)
    create_option(question=question, text="Option A")
    create_option(question=question, text="Option B")
    create_option(question=question, text="Option C")
    create_option(question=question, text="Option D")
    return question


def create_quiz_with_questions(owner, **kwargs):
    quiz = create_quiz(owner=owner, **kwargs)
    create_question_with_options(
        quiz=quiz, title="Question 1", answer="Option A"
    )
    create_question_with_options(
        quiz=quiz, title="Question 2", answer="Option B"
    )
    return quiz


def assert_question_options(test_case, question):
    test_case.assertIn(question["answer"], question["question_options"])
    test_case.assertEqual(len(question["question_options"]), 4)


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


class QuizRetrieveTest(APITestCase):
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

    def test_retrieve_ok(self):
        url = reverse("quiz-detail", args=[self.quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.quiz.id)
        self.assertEqual(response.data["title"], self.quiz.title)
        self.assertEqual(len(response.data["questions"]), 2)
        for question in response.data["questions"]:
            assert_question_options(self, question)

    def test_retrieve_not_found(self):
        url = reverse("quiz-detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_other_user_quiz(self):
        other_quiz = create_quiz_with_questions(
            owner=self.other_user,
            title="Other Quiz",
            video_url="https://youtube.com/2",
        )
        url = reverse("quiz-detail", args=[other_quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_unauthenticated(self):
        self.client.cookies.clear()
        url = reverse("quiz-detail", args=[self.quiz.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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
