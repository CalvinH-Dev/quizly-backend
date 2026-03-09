from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(**kwargs):
    return User.objects.create_user(**kwargs)
