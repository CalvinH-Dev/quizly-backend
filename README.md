# QuizGen

**QuizGen** is a web application that automatically generates quizzes from YouTube videos using AI. Built with Django and Django REST Framework, it provides a REST API for user authentication and quiz management.

> ⚠️ A frontend is required for full project usage — placeholder for future GitHub repo.

---

## 📋 Project Overview

QuizGen enables:
- **Authenticated users** to generate quizzes from any YouTube video via a simple URL input
- **Gemini 2.5 Flash AI** to analyze video transcripts and produce 10 questions with 4 answer options each
- **Users** to manage, update, and delete their generated quizzes

### Key Features
- 🔐 JWT-based authentication with HTTP-only cookie handling
- 🎥 YouTube transcript fetching via `youtube-transcript-api`
- 🤖 AI-powered quiz generation via Gemini 2.5 Flash
- 📝 10 questions per quiz, each with exactly 4 answer options
- 🌍 Automatic language detection (German / English)
- 🛡️ Owner-based permission system

---

## 🚀 Setup — using Python + .venv

### 📍 Create & Activate the Virtual Environment
```bash
python -m venv .venv
```

Activate it:
```bash
source .venv/bin/activate     # macOS / Linux
.venv\Scripts\activate         # Windows
```

### 📥 Install Requirements
```bash
pip install -r requirements.txt
```

### 🔐 Environment Configuration

Create your environment file from the template:
```bash
cp .env.template .env
```

Add the following variables to your `.env` file:
```
SECRET_KEY=your-django-secret-key
GEMINI_API_KEY=your-gemini-api-key
ENV=dev   # Set to "prod" in production
```

Generate a Django secret key at [https://djecrety.ir/](https://djecrety.ir/).  
Obtain a Gemini API key at [https://aistudio.google.com/](https://aistudio.google.com/).  
`COOKIE_SECURE` is automatically set to `True` when `ENV=prod`.

### 🗄️ Database Setup
```bash
python manage.py migrate
```

### 👤 Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### ▶️ Run the Development Server
```bash
python manage.py runserver
```

Admin panel: `http://127.0.0.1:8000/admin/`  
API base URL: `http://127.0.0.1:8000/api/`

---

## 🔑 Authentication

QuizGen uses JWT authentication via `djangorestframework-simplejwt`. Tokens are stored as HTTP-only cookies to prevent XSS attacks.

| Endpoint | Method | Description |
|---|---|---|
| `api/auth/register/` | POST | Register a new user |
| `api/auth/login/` | POST | Login and receive token cookies |
| `api/auth/logout/` | POST | Blacklist refresh token and clear cookies |
| `api/auth/token/refresh/` | POST | Issue a new access token from the refresh cookie |

---

## 🎯 Quiz API

| Endpoint | Method | Description |
|---|---|---|
| `api/quizzes/` | GET | List all quizzes owned by the authenticated user |
| `api/quizzes/` | POST | Generate a new quiz from a YouTube URL |
| `api/quizzes/{id}/` | GET | Retrieve a specific quiz |
| `api/quizzes/{id}/` | PATCH | Update a quiz's title or description |
| `api/quizzes/{id}/` | DELETE | Delete a quiz |

### Quiz Generation Example

```json
POST /api/quizzes/
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

The API will:
1. Extract the video ID from the URL
2. Fetch the transcript via `youtube-transcript-api`
3. Send the transcript to Gemini 2.5 Flash with a structured prompt
4. Parse and validate the returned quiz JSON
5. Persist the quiz, questions, and options to the database

---

## 📝 Data Models

### Quiz
- Belongs to an authenticated user
- Fields: `title`, `description`, `video_url`, `created_at`, `updated_at`

### Question
- Belongs to a `Quiz`
- Must have exactly 4 options
- Fields: `title`, `answer`, `created_at`, `updated_at`

### Option
- Belongs to a `Question`
- A question can have at most 4 options
- Fields: `text`

---

## 👥 Permissions

| Action | Permission |
|---|---|
| Register | Public |
| Login | Public |
| Create quiz | Authenticated |
| View / Edit / Delete quiz | Authenticated + Owner |

---

## 🛠️ Development

### Running Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Running Tests
```bash
python manage.py test
```

---

## 📌 Notes

- **Never commit your `.env` file** — add it to `.gitignore`
- The `db.sqlite3` file is not included; run `migrate` to create a fresh database
- Set `ENV=prod` in production to enable secure cookies (requires HTTPS)
- Transcripts are fetched preferring German (`de`) first, then English (`en`)

---

## 📚 Quick Reference

| Step | Command |
|---|---|
| Create environment | `python -m venv .venv` |
| Activate environment | `source .venv/bin/activate` |
| Install dependencies | `pip install -r requirements.txt` |
| Configure .env | `cp .env.template .env` |
| Create database | `python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Run server | `python manage.py runserver` |
| Run tests | `python manage.py test` |
| Access admin | `http://127.0.0.1:8000/admin/` |
| Access API | `http://127.0.0.1:8000/api/` |

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Welcome to QuizGen!** 🎓🤖

*Turn any YouTube video into an interactive quiz in seconds.*
