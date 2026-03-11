from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from auth_app.api.serializers import (
    CustomTokenObtainPairSerializer,
    RegistrationSerializer,
)


class RegistrationView(APIView):
    """Handle user registration."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Register a new user.

        Args:
            request: Incoming request containing user registration data.

        Returns:
            201 on success, 400 if validation fails.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """Handle user login and set JWT tokens as HTTP-only cookies."""

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Authenticate user and set access/refresh token cookies.

        Args:
            request: Incoming request containing login credentials.

        Returns:
            200 with user info on success, 401 if credentials are invalid.
        """
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.get("refresh")
        access_token = response.data.get("access")
        user = response.data.get("user")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="Lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="Lax",
        )
        response.data = {"detail": "Login successfully!", "user": user}
        return response


class LogoutView(APIView):
    """Handle user logout by blacklisting the refresh token and clearing cookies."""

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Blacklist the refresh token and delete auth cookies.

        Args:
            request: Incoming request containing the refresh token cookie.

        Returns:
            200 on success, 400 if token is missing or invalid.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = Response(
            {
                "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
            },
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh the access token using the refresh token stored in cookies."""

    def post(self, request: Request, *args, **kwargs) -> Response:
        """Issue a new access token cookie from a valid refresh token cookie.

        Args:
            request: Incoming request containing the refresh token cookie.

        Returns:
            200 with new access token cookie, 401 if token is missing or invalid.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"detail": "Refresh token not valid"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get("access")
        response = Response({"detail": "Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="Lax",
        )
        return response
