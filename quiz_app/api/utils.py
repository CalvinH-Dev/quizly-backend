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
