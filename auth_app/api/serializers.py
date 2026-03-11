from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for new user registration."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_confirmed_password(self, value: str) -> str:
        """Check that password and confirmed_password match.

        Args:
            value: The confirmed_password field value.

        Raises:
            ValidationError: If passwords do not match.
        """
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match.")
        return value

    def validate_email(self, value: str) -> str:
        """Check that the email is not already registered.

        Args:
            value: The email field value.

        Raises:
            ValidationError: If the email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def save(self, **kwargs) -> User:
        """Create and return a new user with a hashed password."""
        account = User(
            username=self.validated_data["username"],
            email=self.validated_data["email"],
        )
        account.set_password(self.validated_data["password"])
        account.save()
        return account


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend JWT token response with basic user information."""

    def validate(self, attrs: dict) -> dict:
        """Add user details to the token response payload.

        Args:
            attrs: Raw input attributes containing credentials.

        Returns:
            Token data dict extended with user id, username, and email.
        """
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.pk,
            "username": self.user.username,
            "email": self.user.email,
        }
        return data
