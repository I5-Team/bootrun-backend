"""
영상 재생시간 자동 계산 유틸리티

YouTube URL과 VOD 파일의 재생시간을 자동으로 추출합니다.
"""

import re
import subprocess
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


def extract_youtube_video_id(url: str) -> Optional[str]:
    """
    YouTube URL에서 비디오 ID 추출

    지원하는 형식:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


async def get_youtube_video_duration(video_url: str, api_key: str) -> Optional[int]:
    """
    YouTube API를 사용하여 영상의 재생시간(초)을 가져옵니다.

    Args:
        video_url: YouTube 영상 URL
        api_key: YouTube Data API v3 키

    Returns:
        재생시간(초) 또는 None (실패 시)
    """
    try:
        # YouTube 비디오 ID 추출
        video_id = extract_youtube_video_id(video_url)
        if not video_id:
            logger.warning(f"YouTube URL에서 비디오 ID를 추출할 수 없습니다: {video_url}")
            return None

        # YouTube Data API 호출
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "contentDetails",
            "id": video_id,
            "key": api_key
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        # 응답 검증
        if not data.get("items"):
            logger.warning(f"YouTube API에서 영상을 찾을 수 없습니다: {video_id}")
            return None

        # ISO 8601 duration 파싱 (예: PT1H2M10S -> 3730초)
        duration_str = data["items"][0]["contentDetails"]["duration"]
        duration_seconds = parse_iso8601_duration(duration_str)

        logger.info(f"YouTube 영상 재생시간 추출 성공: {video_id} -> {duration_seconds}초")
        return duration_seconds

    except httpx.HTTPError as e:
        logger.error(f"YouTube API 호출 실패: {e}")
        return None
    except Exception as e:
        logger.error(f"YouTube 재생시간 추출 중 오류: {e}")
        return None


def parse_iso8601_duration(duration: str) -> int:
    """
    ISO 8601 duration 형식을 초 단위로 변환

    예시:
    - PT15M33S -> 933초
    - PT1H2M10S -> 3730초
    - PT5M -> 300초
    """
    pattern = re.compile(
        r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    )
    match = pattern.match(duration)

    if not match:
        return 0

    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    seconds = int(match.group(4) or 0)

    total_seconds = (days * 86400) + (hours * 3600) + (minutes * 60) + seconds
    return total_seconds


async def get_vod_video_duration(video_path: str) -> Optional[int]:
    """
    ffprobe를 사용하여 VOD 파일의 재생시간(초)을 추출합니다.

    Args:
        video_path: VOD 파일 경로 (로컬 파일 또는 S3 URL)

    Returns:
        재생시간(초) 또는 None (실패 시)
    """
    try:
        # ffprobe 명령어 실행
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            logger.error(f"ffprobe 실행 실패: {result.stderr}")
            return None

        # 재생시간 파싱 (소수점 포함될 수 있음)
        duration_str = result.stdout.strip()
        if not duration_str:
            logger.warning(f"ffprobe에서 재생시간을 가져올 수 없습니다: {video_path}")
            return None

        duration_seconds = int(float(duration_str))
        logger.info(f"VOD 영상 재생시간 추출 성공: {video_path} -> {duration_seconds}초")
        return duration_seconds

    except subprocess.TimeoutExpired:
        logger.error(f"ffprobe 실행 타임아웃: {video_path}")
        return None
    except FileNotFoundError:
        logger.error("ffprobe를 찾을 수 없습니다. ffmpeg가 설치되어 있는지 확인하세요.")
        return None
    except Exception as e:
        logger.error(f"VOD 재생시간 추출 중 오류: {e}")
        return None


async def get_video_duration(video_url: str, video_type: str, youtube_api_key: Optional[str] = None) -> Optional[int]:
    """
    영상 URL과 타입에 따라 재생시간을 자동으로 추출합니다.

    Args:
        video_url: 영상 URL
        video_type: 'youtube' 또는 'vod'
        youtube_api_key: YouTube API 키 (YouTube 영상인 경우 필수)

    Returns:
        재생시간(초) 또는 None (실패 시)
    """
    if video_type == "youtube":
        if not youtube_api_key:
            logger.warning("YouTube API 키가 없어 자동 계산을 할 수 없습니다.")
            return None
        return await get_youtube_video_duration(video_url, youtube_api_key)

    elif video_type == "vod":
        return await get_vod_video_duration(video_url)

    else:
        logger.warning(f"지원하지 않는 영상 타입: {video_type}")
        return None
