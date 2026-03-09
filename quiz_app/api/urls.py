from rest_framework.routers import DefaultRouter

from quiz_app.api.views import QuizViewSet

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename="quiz")

urlpatterns = router.urls
