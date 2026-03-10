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
