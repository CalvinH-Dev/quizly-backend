from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# Create your tests here.
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
