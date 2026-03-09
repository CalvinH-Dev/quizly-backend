from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.test_helpers.auth_helpers import create_user


class RegistrationTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user_data = {
            "username": "your_username",
            "password": "your_password",
            "email": "your_email@example.com",
        }

    def test_registration_ok(self):
        url = reverse("registration")
        registration_data = self.user_data
        registration_data["confirmed_password"] = registration_data["password"]
        response = self.client.post(url, registration_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertEqual(data.get("detail"), "User created successfully!")

    def test_registration_bad_request(self):
        url = reverse("registration")

        bad_data = self.user_data.copy()
        bad_data["confirmed_password"] = "wrong_password"
        response = self.client.post(url, bad_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_fields(self):
        url = reverse("registration")

        incomplete_data = {"username": "your_username"}
        response = self.client.post(url, incomplete_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_user(self):
        url = reverse("registration")

        valid_data = self.user_data.copy()
        valid_data["confirmed_password"] = valid_data["password"]
        self.client.post(url, valid_data, format="json")

        response = self.client.post(url, valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email(self):
        url = reverse("registration")

        valid_data = self.user_data.copy()
        valid_data["confirmed_password"] = valid_data["password"]
        self.client.post(url, valid_data, format="json")

        duplicate_email_data = self.user_data.copy()
        duplicate_email_data["username"] = "other_username"
        duplicate_email_data["confirmed_password"] = duplicate_email_data[
            "password"
        ]

        response = self.client.post(url, duplicate_email_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_data = {
            "username": "your_username",
            "password": "your_password",
        }
        register_data = self.login_data.copy()
        register_data["email"] = "your_email@example.com"
        self.user = create_user(**register_data)

    def test_login_ok(self):
        url = reverse("login")
        response = self.client.post(url, self.login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["access_token"].value)
        self.assertTrue(response.cookies["refresh_token"].value)

    def test_login_wrong_password(self):
        url = reverse("login")
        bad_data = self.login_data.copy()
        bad_data["password"] = "wrong_password"
        response = self.client.post(url, bad_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_username(self):
        url = reverse("login")
        bad_data = self.login_data.copy()
        bad_data["username"] = "wrong_username"
        response = self.client.post(url, bad_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_password(self):
        url = reverse("login")
        bad_data = {"username": self.login_data["username"]}
        response = self.client.post(url, bad_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_username(self):
        url = reverse("login")
        bad_data = {"password": self.login_data["password"]}
        response = self.client.post(url, bad_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_body(self):
        url = reverse("login")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_data = {
            "username": "your_username",
            "password": "your_password",
        }
        register_data = self.login_data.copy()
        register_data["email"] = "your_email@example.com"
        self.user = create_user(**register_data)

    def _login(self):
        url = reverse("login")
        response = self.client.post(url, self.login_data, format="json")
        return response

    def test_logout_ok(self):
        self._login()
        url = reverse("logout")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("detail"),
            "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.",
        )
        self.assertFalse(self.client.cookies.get("access_token", "").value)
        self.assertFalse(self.client.cookies.get("refresh_token", "").value)

    def test_logout_unauthenticated(self):
        url = reverse("logout")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_data = {
            "username": "your_username",
            "password": "your_password",
        }
        register_data = self.login_data.copy()
        register_data["email"] = "your_email@example.com"
        self.user = create_user(**register_data)

    def _login(self):
        url = reverse("login")
        return self.client.post(url, self.login_data, format="json")

    def test_refresh_ok(self):
        self._login()
        url = reverse("token_refresh")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertTrue(response.cookies["access_token"].value)
        self.assertEqual(
            response.data.get("detail"),
            "Token refreshed",
        )

    def test_refresh_no_cookie(self):
        url = reverse("token_refresh")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
