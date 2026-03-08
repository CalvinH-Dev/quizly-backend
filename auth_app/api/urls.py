from django.urls import path

from auth_app.api.views import TestView

urlpatterns = [path("index", TestView.as_view())]
