import json

from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

from quiz_app.api.utils import build_quiz_prompt, extract_yt_video_id

ytt_api = YouTubeTranscriptApi()


def fetch_transcript(url: str) -> str:
    video_id = extract_yt_video_id(url)
    if not video_id:
        raise ValueError("Invalid or missing YouTube URL.")
    return get_transcript_as_json(video_id, ["de", "en"])


def get_transcript_as_json(video_id, languages=["en"]):
    formatter = JSONFormatter()
    fetched_transcript = ytt_api.fetch(video_id, languages=languages)
    json_formatted = formatter.format_transcript(fetched_transcript)

    return json_formatted


def generate_quiz_from_json_transcript(transcript_json: str) -> dict:
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
