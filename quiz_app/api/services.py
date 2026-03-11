import json

from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

from quiz_app.api.utils import build_quiz_prompt, extract_yt_video_id

ytt_api = YouTubeTranscriptApi()


def fetch_transcript(url: str) -> str:
    """Fetch the transcript for a YouTube video as a JSON string.

    Args:
        url: The YouTube video URL.

    Returns:
        The transcript formatted as a JSON string.

    Raises:
        ValueError: If the URL is invalid or no video ID can be extracted.
    """
    video_id = extract_yt_video_id(url)
    if not video_id:
        raise ValueError("Invalid or missing YouTube URL.")
    return get_transcript_as_json(video_id, ["de", "en"])


def get_transcript_as_json(
    video_id: str, languages: list[str] = ["en"]
) -> str:
    """Fetch and format a video transcript as a JSON string.

    Args:
        video_id: The YouTube video ID.
        languages: Preferred transcript languages in order of priority.

    Returns:
        The transcript as a JSON-formatted string.
    """
    formatter = JSONFormatter()
    fetched_transcript = ytt_api.fetch(video_id, languages=languages)
    return formatter.format_transcript(fetched_transcript)


def generate_quiz_from_json_transcript(transcript_json: str) -> dict:
    """Send a transcript to Gemini and return the generated quiz as a dict.

    Args:
        transcript_json: The video transcript as a JSON string.

    Returns:
        The parsed quiz dictionary containing title, description, and questions.

    Raises:
        json.JSONDecodeError: If the Gemini response cannot be parsed as JSON.
    """
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_quiz_prompt(transcript_json),
    )
    cleaned = (
        response.text.strip()
        .removeprefix("```json")
        .removesuffix("```")
        .strip()
    )
    return json.loads(cleaned)
