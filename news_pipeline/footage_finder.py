#!/usr/bin/env python3
"""Search and download real footage clips for AI news video segments.

For 2 items per video, finds YouTube/Bilibili clips or web screenshots
to replace animated HTML cards, making the video feel more like a real
tech news production.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# ── Paths ──────────────────────────────────────────────────

YT_DLP = "/Library/Frameworks/Python.framework/Versions/3.14/bin/yt-dlp"
FFMPEG = str(Path.home() / "Library/Application Support/bilibili/ffmpeg/ffmpeg")
PROJECT_DIR = Path(__file__).resolve().parent.parent

FOOTAGE_PER_VIDEO = 99  # process all items
MAX_CLIP_SECONDS = 20
CACHE_TTL_DAYS = 7

# ── Data ───────────────────────────────────────────────────

@dataclass
class FootageResult:
    item_index: int
    source_type: str = "none"   # "youtube" | "bilibili" | "web_screenshot" | "none"
    video_path: Optional[Path] = None
    duration: float = 0.0
    source_url: str = ""
    confidence: float = 0.0
    error: str = ""


# ── Candidates ─────────────────────────────────────────────

def _select_footage_candidates(items: list[dict]) -> list[int]:
    """Return indices of up to 2 items with highest visual potential."""
    scores = []
    for i, item in enumerate(items):
        title = item.get("title", "")
        source = item.get("source_note", "").lower()
        summary = item.get("summary", "")
        is_github = "github" in source

        score = 0
        # Strong visual signals
        if any(kw in source for kw in ("openai", "google", "meta", "anthropic",
                                         "demo", "launch", "release", "youtube")):
            score += 3
        # Product / tool announcements
        if any(kw in (title + summary).lower()
               for kw in ("发布", "上线", "开源", "推出", "demo", "product", "tool")):
            score += 2
        # GitHub repos have README screenshots
        if is_github:
            score += 2
        # Big company news
        if any(name in (title + source)
               for name in ("GPT", "Claude", "Gemini", "Meta", "NVIDIA", "Kimi", "DeepSeek")):
            score += 2
        # Penalize pure policy / text-only news
        if any(kw in (title + summary)
               for kw in ("公开信", "政策", "监管", "报告", "声明", "融资")):
            score -= 1

        scores.append((score, i))

    scores.sort(key=lambda x: -x[0])
    # Return top 2 with positive scores, fallback to first 2
    result = [i for s, i in scores]  # all items
    return result


# ── Search ─────────────────────────────────────────────────

def _generate_search_queries(item: dict) -> list[str]:
    """Generate search queries for an item, prioritizing English for YouTube."""
    title = item.get("title", "")
    source = item.get("source_note", "")
    summary = item.get("summary", "")

    # Extract English keywords from title + summary
    en_words = re.findall(r'[A-Za-z]{2,}(?:\s+[A-Za-z]{2,})*', title + " " + summary)
    en_keywords = ' '.join(en_words[:5]) if en_words else ''

    # Base queries: source + English keywords (best for YouTube)
    queries = []
    if source and en_keywords:
        queries.append(f"{source} {en_keywords}")
    if en_keywords:
        queries.append(en_keywords)
    # Fallback: Chinese search
    cn = re.sub(r'[^\w\s一-鿿]', ' ', title)
    cn_words = cn.split()
    if cn_words:
        queries.append(' '.join(cn_words[:4]))

    return [q for q in queries if len(q) > 5][:3]


def _search_youtube(query: str, max_results: int = 5) -> list[dict]:
    """Search YouTube via yt-dlp, return video info list."""
    try:
        result = subprocess.run(
            [YT_DLP, f"ytsearch{max_results}:{query}",
             "--dump-json", "--no-download", "--flat-playlist",
             "--no-warnings", "--ignore-errors"],
            capture_output=True, text=True, timeout=20,
        )
        videos = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                videos.append({
                    "title": data.get("title", ""),
                    "url": data.get("webpage_url", data.get("url", "")),
                    "duration": data.get("duration", 0) or 0,
                    "view_count": data.get("view_count", 0) or 0,
                    "channel": data.get("channel", data.get("uploader", "")),
                    "id": data.get("id", ""),
                })
            except json.JSONDecodeError:
                continue
        return videos
    except Exception:
        return []


def _search_bilibili(query: str, max_results: int = 5) -> list[dict]:
    """Search Bilibili via yt-dlp."""
    try:
        result = subprocess.run(
            [YT_DLP, f"bilisearch{max_results}:{query}",
             "--dump-json", "--no-download", "--flat-playlist",
             "--no-warnings", "--ignore-errors"],
            capture_output=True, text=True, timeout=20,
        )
        videos = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                videos.append({
                    "title": data.get("title", ""),
                    "url": data.get("webpage_url", data.get("url", "")),
                    "duration": data.get("duration", 0) or 0,
                    "view_count": data.get("view_count", 0) or 0,
                    "channel": data.get("channel", data.get("uploader", "")),
                    "id": data.get("id", ""),
                })
            except json.JSONDecodeError:
                continue
        return videos
    except Exception:
        return []


def _score_video_match(video: dict, item: dict) -> float:
    """Score how well a video matches a news item (0.0-1.0)."""
    v_title = video.get("title", "").lower()
    i_title = item.get("title", "").lower()
    i_summary = item.get("summary", "").lower()
    i_source = item.get("source_note", "").lower()

    score = 0.0

    # Keyword overlap
    i_words = set(re.findall(r'\w+', i_title + " " + i_summary))
    v_words = set(re.findall(r'\w+', v_title))
    if i_words:
        overlap = len(i_words & v_words) / len(i_words)
        score += overlap * 0.4

    # Source name in video title (e.g., "OpenAI" in video about GPT)
    if i_source and i_source in v_title:
        score += 0.2

    # Channel quality: prefer official / known tech channels
    channel = video.get("channel", "").lower()
    official_channels = ("openai", "google", "meta", "anthropic", "nvidia",
                         "microsoft", "android", "apple", "hugging face",
                         "moonshot", "mistral", "deepseek", "anthropicclaude")
    if any(ch in channel for ch in official_channels):
        score += 0.3

    # Penalize AI news roundup / secondary aggregation channels
    roundup_keywords = ("ai news roundup", "weekly ai recap", "ai weekly digest",
                        "top ai stories", "ai news update")
    if any(rk in v_title for rk in roundup_keywords):
        score -= 0.5
    roundup_channels = ("woeeater", "aibreakdown", "ai news daily",
                        "the ai daily", "tech news weekly")
    if any(rc in channel for rc in roundup_channels):
        score -= 0.5

    # Duration: prefer 30s-10min (demos, announcements, not podcasts)
    dur = video.get("duration", 0)
    if 30 <= dur <= 600:
        score += 0.1
    elif dur > 3600:  # Livestreams, long talks
        score -= 0.2

    # Penalize non-tech keywords
    penalty_kw = ("livestream", "podcast", "interview", "reaction", "reacts",
                  "vlog", "unboxing", "prank", "game", "music video", "trailer")
    if any(pk in v_title for pk in penalty_kw):
        score -= 0.3

    return max(0.0, min(1.0, score))


# ── Download ───────────────────────────────────────────────

def _download_clip(
    video_url: str,
    output_dir: Path,
    target_duration: float,
    target_w: int = 1920,
    target_h: int = 1080,
) -> Optional[Path]:
    """Download a clip from a video URL and crop to fill target dimensions."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "raw.mp4"
    processed_path = output_dir / "clip.mp4"

    if processed_path.exists():
        return processed_path

    clip_dur = min(target_duration + 3, MAX_CLIP_SECONDS)

    try:
        # yt-dlp: download best quality <= 720p
        subprocess.run(
            [YT_DLP, "-f", "best[height<=720]",
             "--download-sections", f"*0-{int(clip_dur)}",
             "-o", str(raw_path),
             "--no-warnings", "--no-playlist",
             video_url],
            capture_output=True, text=True, timeout=60,
        )

        if not raw_path.exists():
            # Try without --download-sections (some sites don't support it)
            subprocess.run(
                [YT_DLP, "-f", "best[height<=720]",
                 "-o", str(raw_path),
                 "--no-warnings", "--no-playlist",
                 video_url],
                capture_output=True, text=True, timeout=60,
            )

        if not raw_path.exists():
            return None

        # FFmpeg: scale fill + crop to target, trim to exact duration
        subprocess.run([
            FFMPEG, "-y", "-i", str(raw_path),
            "-t", str(target_duration),
            "-vf", (f"scale={target_w}:{target_h}"
                    ":force_original_aspect_ratio=increase"
                    f",crop={target_w}:{target_h}"),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-an",  # no original audio
            str(processed_path),
        ], capture_output=True, text=True, timeout=30)

        # Clean up raw
        raw_path.unlink(missing_ok=True)

        if processed_path.exists():
            return processed_path
        return None

    except Exception:
        return None


# ── Cache ──────────────────────────────────────────────────

def _screenshot_github_repo(item: dict, output_dir: Path, target_w: int = 1920, target_h: int = 1080) -> Optional[Path]:
    """Take a Playwright screenshot of a GitHub repo page, return path to PNG."""
    title = item.get("title", "")
    source = item.get("source_note", "")

    # Try explicit repo field first, then parse from title/source
    repo = item.get("repo", "")
    if not repo:
        for pattern in [r'([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', r'github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)']:
            m = re.search(pattern, title + " " + source)
            if m:
                repo = m.group(1)
                break

    if not repo:
        return None

    url = f"https://github.com/{repo}"
    png_path = output_dir / "screenshot.png"
    if png_path.exists():
        return png_path

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": target_w, "height": target_h})
            page.goto(url, wait_until="load", timeout=15000)
            page.wait_for_timeout(2000)  # wait for README to render
            page.screenshot(path=png_path, full_page=False)
            browser.close()
        if png_path.exists():
            return png_path
    except Exception:
        pass
    return None


def _screenshot_to_video(png_path: Path, output_dir: Path, duration: float,
                          target_w: int = 1920, target_h: int = 1080) -> Optional[Path]:
    """Convert a static screenshot to a short video with slow zoom (Ken Burns effect)."""
    clip_path = output_dir / "clip.mp4"
    if clip_path.exists():
        return clip_path

    try:
        subprocess.run([
            FFMPEG, "-y", "-loop", "1", "-i", str(png_path),
            "-t", str(duration),
            "-vf", (f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                    f"crop={target_w}:{target_h},"
                    f"zoompan=z='min(zoom+0.001,1.1)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-an",
            str(clip_path),
        ], capture_output=True, text=True, timeout=30)
        if clip_path.exists():
            return clip_path
    except Exception:
        pass
    return None


def _item_hash(item: dict) -> str:
    """Stable hash for an item based on title + source."""
    key = (item.get("title", "")[:80] + "|" + item.get("source_note", ""))
    return hashlib.md5(key.encode()).hexdigest()[:12]


def _load_cached_result(cache_dir: Path, item_hash: str) -> Optional[FootageResult]:
    """Load cached footage result if still valid."""
    result_json = cache_dir / item_hash / "result.json"
    if not result_json.exists():
        return None

    try:
        data = json.loads(result_json.read_text())
        cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
        age = datetime.now(timezone.utc) - cached_at.replace(tzinfo=timezone.utc)

        if age > timedelta(days=CACHE_TTL_DAYS):
            return None

        clip_path = cache_dir / item_hash / "clip.mp4"
        if data.get("source_type") != "none" and not clip_path.exists():
            return None  # cache invalid, file missing

        return FootageResult(
            item_index=data.get("item_index", 0),
            source_type=data.get("source_type", "none"),
            video_path=clip_path if clip_path.exists() else None,
            duration=data.get("duration", 0),
            source_url=data.get("source_url", ""),
            confidence=data.get("confidence", 0),
        )
    except Exception:
        return None


def _save_cached_result(cache_dir: Path, item_hash: str, result: FootageResult):
    """Save footage result to cache."""
    item_dir = cache_dir / item_hash
    item_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "item_index": result.item_index,
        "source_type": result.source_type,
        "duration": result.duration,
        "source_url": result.source_url,
        "confidence": result.confidence,
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }
    (item_dir / "result.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))


# ── Main ───────────────────────────────────────────────────

def find_footage_for_items(
    items: list[dict],
    output_dir: Path,
) -> dict[int, FootageResult]:
    """Find real footage for up to 2 items. Returns {item_index: FootageResult}.

    Non-blocking: all failures are caught and returned as source_type="none".
    """
    cache_dir = output_dir / "footage_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    candidates = _select_footage_candidates(items)
    if not candidates:
        return {}

    results: dict[int, FootageResult] = {}

    for idx in candidates:
        item = items[idx]
        ihash = _item_hash(item)

        # Check cache first
        cached = _load_cached_result(cache_dir, ihash)
        if cached is not None:
            cached.item_index = idx + 1  # 1-based for video pipeline
            results[idx + 1] = cached
            print(f"  [footage] item {idx+1}: cached ({cached.source_type}, conf={cached.confidence:.1f})")
            continue

        # Find footage
        print(f"  [footage] item {idx+1}: searching...")
        result = _find_single_item_footage(item, idx + 1, cache_dir, ihash)

        # Save to cache
        _save_cached_result(cache_dir, ihash, result)
        results[idx + 1] = result

        if result.source_type != "none":
            print(f"  [footage] item {idx+1}: ✓ {result.source_type} (conf={result.confidence:.1f}) {result.source_url[:60]}")
        else:
            print(f"  [footage] item {idx+1}: ✗ no footage found ({result.error})")

    return results


def _find_single_item_footage(
    item: dict,
    item_index: int,
    cache_dir: Path,
    ihash: str,
) -> FootageResult:
    """Find and download footage for a single item."""
    clip_dir = cache_dir / ihash
    is_github = "github" in item.get("source_note", "").lower()

    # GitHub items: screenshot repo page
    if is_github:
        png = _screenshot_github_repo(item, clip_dir)
        if png:
            clip = _screenshot_to_video(png, clip_dir, duration=10.0)
            if clip:
                return FootageResult(
                    item_index=item_index,
                    source_type="github_screenshot",
                    video_path=clip,
                    duration=10.0,
                    source_url="",
                    confidence=0.8,
                )
        return FootageResult(item_index=item_index, source_type="none",
                             error="github screenshot failed")

    # Non-GitHub items: YouTube / Bilibili search
    queries = _generate_search_queries(item)
    best_video = None
    best_score = 0.0
    best_source = "none"

    for query in queries:
        yt_results = _search_youtube(query)
        for v in yt_results:
            s = _score_video_match(v, item)
            if s > best_score:
                best_score = s
                best_video = v
                best_source = "youtube"

    if best_score < 0.3:
        for query in queries:
            bl_results = _search_bilibili(query)
            for v in bl_results:
                s = _score_video_match(v, item)
                if s > best_score:
                    best_score = s
                    best_video = v
                    best_source = "bilibili"

    if best_video and best_score >= 0.1 and best_video.get("url"):
        clip_dur = min(15.0, best_video.get("duration", 60) * 0.3)
        clip_path = _download_clip(best_video["url"], clip_dir,
                                   target_duration=clip_dur)
        if clip_path:
            return FootageResult(
                item_index=item_index,
                source_type=best_source,
                video_path=clip_path,
                duration=clip_dur,
                source_url=best_video.get("url", ""),
                confidence=best_score,
            )

    return FootageResult(
        item_index=item_index,
        source_type="none",
        error="no matching video found" if not best_video else "download failed",
    )
