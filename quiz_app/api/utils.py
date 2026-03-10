import re
from urllib.parse import ParseResult, parse_qs, urlparse


def is_youtube_url(parsed: ParseResult) -> bool:
    host = parsed.netloc.lower().removeprefix("www.").removeprefix("m.")
    return host in ("youtube.com", "youtu.be")


def get_host(parsed: ParseResult) -> str:
    return parsed.netloc.lower().removeprefix("www.").removeprefix("m.")


def validate_video_id(video_id: str | None) -> str | None:
    if video_id and re.fullmatch(r"[\w-]{11}", video_id):
        return video_id
    return None


def extract_from_short_url(parsed: ParseResult) -> str | None:
    """youtu.be/VIDEO_ID"""
    video_id = parsed.path.lstrip("/").split("/")[0]
    return validate_video_id(video_id)


def extract_from_watch_url(parsed: ParseResult) -> str | None:
    """youtube.com/watch?v=VIDEO_ID"""
    video_id = parse_qs(parsed.query).get("v", [None])[0]
    return validate_video_id(video_id)


def extract_from_shorts_url(parsed: ParseResult) -> str | None:
    """youtube.com/shorts/VIDEO_ID"""
    video_id = parsed.path.split("/")[2]
    return validate_video_id(video_id)


def extract_from_embed_url(parsed: ParseResult) -> str | None:
    """youtube.com/embed/VIDEO_ID or /v/VIDEO_ID"""
    video_id = parsed.path.split("/")[2]
    return validate_video_id(video_id)


def extract_yt_video_id(url: str) -> str | None:
    if not url or not isinstance(url, str):
        return None

    parsed = urlparse(url.strip())

    if not is_youtube_url(parsed):
        return None

    host = get_host(parsed)

    if host == "youtu.be":
        return extract_from_short_url(parsed)

    if parsed.path == "/watch":
        return extract_from_watch_url(parsed)

    if parsed.path.startswith("/shorts/"):
        return extract_from_shorts_url(parsed)

    if re.match(r"^/(embed|v)/", parsed.path):
        return extract_from_embed_url(parsed)

    return None


def build_quiz_prompt(transcript_json: str) -> str:
    return f"""Based on the following transcript, generate a quiz in valid JSON format.
                The quiz must follow this exact structure:
                {{
                "title": "Create a concise quiz title based on the topic of the transcript.",
                "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
                "questions": [
                    {{
                    "question_title": "The question goes here.",
                    "question_options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "The correct answer from the above options"
                    }},
                    (exactly 10 questions)
                ]
                }}
                Requirements:
                - Each question must have exactly 4 distinct answer options.
                - Only one correct answer is allowed per question, and it must be present in 'question_options'.
                - The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
                - Do not include explanations, comments, or any text outside the JSON.
                - Use german if the transcript is in german, else english

                Transcript:
                {transcript_json}"""
