from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from auth_app.api.views import LoginView, RegistrationView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    # path("logout/", name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
