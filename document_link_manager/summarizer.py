"""
Content Summarizer - Fetches and summarizes content from URLs.

Uses web scraping to extract content and generates summaries.
"""

import re
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import html


@dataclass
class ContentCache:
    """Cache entry for fetched content."""
    url: str
    content: str
    title: str
    summary: str
    fetched_at: str
    expires_at: str


class ContentSummarizer:
    """
    Summarizes content from URLs.

    Features:
    - Fetch content from various platforms
    - Generate concise summaries
    - Cache results to avoid re-fetching
    - Extract key points and themes
    """

    # Platform-specific content extractors
    SUMMARY_TEMPLATES = {
        "linkedin": "LinkedIn {content_type} about {topic}. Key points: {key_points}",
        "twitter": "Thread/Tweet discussing {topic}. Main message: {key_points}",
        "youtube": "Video covering {topic}. Topics discussed: {key_points}",
        "medium": "Article on {topic}. Main takeaways: {key_points}",
        "substack": "Newsletter about {topic}. Key insights: {key_points}",
        "github": "Repository/code for {topic}. Purpose: {key_points}",
        "default": "{topic}. Summary: {key_points}",
    }

    def __init__(self, cache_dir: Optional[Path] = None, cache_ttl_hours: int = 24):
        """
        Initialize the summarizer.

        Args:
            cache_dir: Directory for caching fetched content
            cache_ttl_hours: Cache time-to-live in hours
        """
        self.cache_dir = cache_dir or Path.home() / ".star_app" / "cache"
        self.cache_ttl_hours = cache_ttl_hours
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, url: str) -> Path:
        """Get the cache file path for a URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.json"

    def _load_from_cache(self, url: str) -> Optional[ContentCache]:
        """Load content from cache if available and not expired."""
        cache_path = self._get_cache_path(url)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            cache = ContentCache(**data)

            # Check if expired
            expires = datetime.fromisoformat(cache.expires_at)
            if datetime.now() > expires:
                cache_path.unlink()  # Remove expired cache
                return None

            return cache
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def _save_to_cache(self, cache: ContentCache):
        """Save content to cache."""
        cache_path = self._get_cache_path(cache.url)

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump({
                "url": cache.url,
                "content": cache.content,
                "title": cache.title,
                "summary": cache.summary,
                "fetched_at": cache.fetched_at,
                "expires_at": cache.expires_at,
            }, f, indent=2)

    def extract_text_from_html(self, html_content: str) -> tuple[str, str]:
        """
        Extract readable text and title from HTML.

        Args:
            html_content: Raw HTML content

        Returns:
            Tuple of (title, text_content)
        """
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""
        title = html.unescape(title)

        # Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)

        # Decode HTML entities
        text = html.unescape(text)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return title, text

    def extract_key_points(self, text: str, max_points: int = 3) -> list[str]:
        """
        Extract key points from text content.

        This is a simple extraction based on sentence analysis.
        In production, you'd want to use an AI model for better summaries.

        Args:
            text: The text to analyze
            max_points: Maximum number of key points

        Returns:
            List of key point strings
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if not sentences:
            return ["Content summary not available"]

        # Score sentences by length and position (simplified heuristic)
        scored = []
        for i, sentence in enumerate(sentences[:50]):  # Limit to first 50 sentences
            # Prefer earlier sentences and medium length
            length_score = min(len(sentence) / 100, 1.0)  # Favor ~100 char sentences
            position_score = 1.0 - (i / 50)  # Earlier is better

            # Bonus for sentences with key indicator words
            indicator_words = ['important', 'key', 'main', 'essential', 'critical',
                             'announce', 'launch', 'introduce', 'reveal', 'discover']
            indicator_bonus = 0.2 if any(w in sentence.lower() for w in indicator_words) else 0

            score = length_score * 0.3 + position_score * 0.5 + indicator_bonus
            scored.append((score, sentence))

        # Sort by score and take top N
        scored.sort(reverse=True)
        key_points = [s[1] for s in scored[:max_points]]

        # Truncate long sentences
        key_points = [
            (p[:150] + "...") if len(p) > 150 else p
            for p in key_points
        ]

        return key_points

    def detect_topic(self, text: str, title: str = "") -> str:
        """
        Detect the main topic from content.

        Args:
            text: Content text
            title: Content title (used as hint)

        Returns:
            Detected topic string
        """
        # Use title as primary topic hint
        if title:
            # Clean up common title patterns
            topic = re.sub(r'\s*[|\-–]\s*.+$', '', title)  # Remove site name suffix
            topic = re.sub(r'^.+\s*[|\-–]\s*', '', topic)  # Remove site name prefix
            if len(topic) > 10 and len(topic) < 100:
                return topic.strip()

        # Fall back to first meaningful sentence
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if 20 < len(sentence) < 200:
                return sentence

        return "this content"

    def generate_summary(
        self,
        text: str,
        title: str,
        platform: str = "default",
        content_type: str = "article"
    ) -> str:
        """
        Generate a summary of the content.

        Args:
            text: The extracted text content
            title: The content title
            platform: The source platform
            content_type: Type of content (article, post, video, etc.)

        Returns:
            Generated summary string
        """
        # Detect topic
        topic = self.detect_topic(text, title)

        # Extract key points
        key_points = self.extract_key_points(text)
        key_points_str = "; ".join(key_points)

        # Get template
        template = self.SUMMARY_TEMPLATES.get(platform, self.SUMMARY_TEMPLATES["default"])

        # Generate summary
        summary = template.format(
            content_type=content_type,
            topic=topic,
            key_points=key_points_str
        )

        # Ensure reasonable length
        if len(summary) > 500:
            summary = summary[:497] + "..."

        return summary

    def summarize_url(
        self,
        url: str,
        platform: str = "default",
        content_type: str = "article",
        force_refresh: bool = False
    ) -> tuple[str, str]:
        """
        Fetch and summarize content from a URL.

        Note: This method returns a placeholder since actual web fetching
        requires external HTTP libraries. In production, integrate with
        requests, httpx, or aiohttp.

        Args:
            url: URL to fetch and summarize
            platform: Source platform
            content_type: Type of content
            force_refresh: Bypass cache

        Returns:
            Tuple of (title, summary)
        """
        # Check cache first
        if not force_refresh:
            cached = self._load_from_cache(url)
            if cached:
                return cached.title, cached.summary

        # For now, return a placeholder
        # In production, you would:
        # 1. Fetch the URL with requests/httpx
        # 2. Extract content based on platform
        # 3. Generate summary
        parsed = urlparse(url)

        title = f"Content from {parsed.netloc}"
        summary = f"[Summary pending] Link from {platform} ({content_type})"

        # Save to cache
        now = datetime.now()
        cache = ContentCache(
            url=url,
            content="",
            title=title,
            summary=summary,
            fetched_at=now.isoformat(),
            expires_at=(now + timedelta(hours=self.cache_ttl_hours)).isoformat()
        )
        self._save_to_cache(cache)

        return title, summary

    def summarize_from_content(
        self,
        content: str,
        url: str,
        platform: str = "default",
        content_type: str = "article"
    ) -> tuple[str, str]:
        """
        Generate summary from provided content (when content is already fetched).

        Args:
            content: HTML or text content
            url: Source URL (for caching)
            platform: Source platform
            content_type: Type of content

        Returns:
            Tuple of (title, summary)
        """
        # Check if content looks like HTML
        if '<html' in content.lower() or '<body' in content.lower():
            title, text = self.extract_text_from_html(content)
        else:
            title = ""
            text = content

        # Generate summary
        summary = self.generate_summary(text, title, platform, content_type)

        # Cache the result
        now = datetime.now()
        cache = ContentCache(
            url=url,
            content=text[:10000],  # Limit cached content size
            title=title,
            summary=summary,
            fetched_at=now.isoformat(),
            expires_at=(now + timedelta(hours=self.cache_ttl_hours)).isoformat()
        )
        self._save_to_cache(cache)

        return title, summary

    def batch_summarize(
        self,
        urls: list[str],
        force_refresh: bool = False
    ) -> dict[str, tuple[str, str]]:
        """
        Summarize multiple URLs.

        Args:
            urls: List of URLs to summarize
            force_refresh: Bypass cache

        Returns:
            Dict mapping URL to (title, summary) tuples
        """
        results = {}
        for url in urls:
            try:
                title, summary = self.summarize_url(url, force_refresh=force_refresh)
                results[url] = (title, summary)
            except Exception as e:
                results[url] = ("Error", f"Failed to summarize: {str(e)}")

        return results

    def clear_cache(self, older_than_hours: Optional[int] = None):
        """
        Clear the content cache.

        Args:
            older_than_hours: Only clear entries older than this (None = all)
        """
        if not self.cache_dir.exists():
            return

        cutoff = None
        if older_than_hours:
            cutoff = datetime.now() - timedelta(hours=older_than_hours)

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if cutoff:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    fetched = datetime.fromisoformat(data["fetched_at"])
                    if fetched > cutoff:
                        continue

                cache_file.unlink()
            except (json.JSONDecodeError, KeyError, OSError):
                # Remove corrupted cache files
                try:
                    cache_file.unlink()
                except OSError:
                    pass


class ManualSummaryHelper:
    """
    Helper for creating manual summaries with templates and suggestions.

    Useful when automatic summarization isn't available or adequate.
    """

    SUMMARY_PROMPTS = {
        "article": [
            "What is the main argument or thesis?",
            "What are the key takeaways?",
            "Why is this relevant to my work?",
        ],
        "post": [
            "What is the main point?",
            "What action or insight does it suggest?",
        ],
        "video": [
            "What topics are covered?",
            "What are the main lessons or insights?",
        ],
        "profile": [
            "Who is this person/company?",
            "Why are they relevant?",
        ],
        "repository": [
            "What does this code/project do?",
            "How might it be useful?",
        ],
    }

    @classmethod
    def get_prompts(cls, content_type: str) -> list[str]:
        """Get summary prompts for a content type."""
        return cls.SUMMARY_PROMPTS.get(content_type, cls.SUMMARY_PROMPTS["article"])

    @classmethod
    def format_summary(cls, answers: dict[str, str]) -> str:
        """
        Format answers into a summary.

        Args:
            answers: Dict mapping prompts to answers

        Returns:
            Formatted summary string
        """
        parts = []
        for question, answer in answers.items():
            if answer:
                parts.append(answer.strip())

        return " ".join(parts)
