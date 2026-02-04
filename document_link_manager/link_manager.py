"""
Link Manager - Core module for managing hyperlinks in documents.

Handles link extraction, validation, and management operations.
"""

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse, parse_qs

from .document import Document, DocumentEntry, EntryCategory


@dataclass
class LinkInfo:
    """Parsed information about a URL."""
    url: str
    domain: str
    platform: str  # linkedin, twitter, youtube, etc.
    content_type: str  # article, post, video, profile, etc.
    clean_url: str  # URL without tracking parameters


class LinkManager:
    """
    Manages links in the CEO's weekly document.

    Features:
    - Extract and clean URLs
    - Detect platform and content type
    - Add links with automatic categorization
    - Batch link processing
    """

    # Known platforms and their patterns
    PLATFORM_PATTERNS = {
        "linkedin": {
            "domains": ["linkedin.com", "www.linkedin.com"],
            "types": {
                r"/posts/": "post",
                r"/pulse/": "article",
                r"/in/": "profile",
                r"/company/": "company",
                r"/jobs/": "job",
            }
        },
        "twitter": {
            "domains": ["twitter.com", "x.com", "www.twitter.com", "www.x.com"],
            "types": {
                r"/status/": "tweet",
                r"^/\w+$": "profile",
            }
        },
        "youtube": {
            "domains": ["youtube.com", "www.youtube.com", "youtu.be"],
            "types": {
                r"/watch": "video",
                r"/playlist": "playlist",
                r"/channel/": "channel",
                r"^/@": "channel",
            }
        },
        "medium": {
            "domains": ["medium.com", "*.medium.com"],
            "types": {
                r".*": "article",
            }
        },
        "github": {
            "domains": ["github.com", "www.github.com"],
            "types": {
                r"/issues/": "issue",
                r"/pull/": "pull_request",
                r"/blob/": "code",
                r"^/[\w-]+/[\w-]+$": "repository",
            }
        },
        "substack": {
            "domains": ["substack.com", "*.substack.com"],
            "types": {
                r"/p/": "article",
            }
        },
    }

    # Tracking parameters to remove
    TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "fbclid", "gclid", "dclid", "msclkid",
        "ref", "source", "referer",
        "mc_eid", "mc_cid",
        "_ga", "_gl",
        "rcm",  # LinkedIn tracking
    }

    def __init__(self, document: Optional[Document] = None):
        """
        Initialize the LinkManager.

        Args:
            document: Optional Document to manage. Can be set later.
        """
        self.document = document

    def set_document(self, document: Document):
        """Set the document to manage."""
        self.document = document

    def parse_url(self, url: str) -> LinkInfo:
        """
        Parse a URL and extract relevant information.

        Args:
            url: The URL to parse

        Returns:
            LinkInfo with parsed details
        """
        # Clean and normalize the URL
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove www. prefix for comparison
        domain_clean = domain.replace("www.", "")

        # Detect platform
        platform = "web"
        content_type = "article"

        for plat_name, plat_info in self.PLATFORM_PATTERNS.items():
            domains = plat_info["domains"]
            if any(domain_clean == d.replace("www.", "").replace("*.", "")
                   or domain_clean.endswith("." + d.replace("*.", ""))
                   for d in domains):
                platform = plat_name

                # Detect content type
                for pattern, c_type in plat_info["types"].items():
                    if re.search(pattern, parsed.path):
                        content_type = c_type
                        break
                break

        # Clean URL by removing tracking parameters
        clean_url = self._clean_url(url)

        return LinkInfo(
            url=url,
            domain=domain,
            platform=platform,
            content_type=content_type,
            clean_url=clean_url
        )

    def _clean_url(self, url: str) -> str:
        """Remove tracking parameters from URL."""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # Remove tracking params
        clean_params = {
            k: v for k, v in params.items()
            if k.lower() not in self.TRACKING_PARAMS
        }

        # Rebuild query string
        if clean_params:
            query_string = "&".join(
                f"{k}={v[0]}" for k, v in clean_params.items()
            )
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if query_string:
                clean_url += f"?{query_string}"
        else:
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        return clean_url

    def extract_urls(self, text: str) -> list[str]:
        """
        Extract all URLs from a block of text.

        Args:
            text: Text containing URLs

        Returns:
            List of extracted URLs
        """
        # URL pattern that handles most common formats
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)

        # Clean up trailing punctuation
        cleaned_urls = []
        for url in urls:
            # Remove trailing punctuation that's likely not part of URL
            url = re.sub(r'[.,;:!?)]+$', '', url)
            cleaned_urls.append(url)

        return list(set(cleaned_urls))  # Remove duplicates

    def suggest_category(self, link_info: LinkInfo) -> str:
        """
        Suggest a category based on link information.

        Args:
            link_info: Parsed link information

        Returns:
            Suggested category string
        """
        # Map content types to categories
        type_to_category = {
            "article": EntryCategory.READING.value,
            "post": EntryCategory.READING.value,
            "video": EntryCategory.READING.value,
            "tweet": EntryCategory.READING.value,
            "profile": EntryCategory.REFERENCE.value,
            "company": EntryCategory.REFERENCE.value,
            "repository": EntryCategory.REFERENCE.value,
            "code": EntryCategory.REFERENCE.value,
            "issue": EntryCategory.ACTION_ITEM.value,
            "pull_request": EntryCategory.ACTION_ITEM.value,
            "job": EntryCategory.REFERENCE.value,
        }

        return type_to_category.get(
            link_info.content_type,
            EntryCategory.OTHER.value
        )

    def suggest_section(self, link_info: LinkInfo) -> str:
        """
        Suggest a document section based on link information.

        Args:
            link_info: Parsed link information

        Returns:
            Suggested section key
        """
        # Map content types to sections
        type_to_section = {
            "article": "reading_list",
            "post": "reading_list",
            "video": "reading_list",
            "tweet": "reading_list",
            "profile": "references",
            "company": "references",
            "repository": "references",
            "code": "references",
            "issue": "action_items",
            "pull_request": "action_items",
        }

        return type_to_section.get(link_info.content_type, "this_week")

    def add_link(
        self,
        url: str,
        title: str,
        summary: str = "",
        section: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[list] = None,
        source: str = "",
        priority: int = 0
    ) -> Optional[DocumentEntry]:
        """
        Add a new link to the document.

        Args:
            url: The URL to add
            title: Title for the link
            summary: Summary/description of the content
            section: Document section (auto-detected if not provided)
            category: Entry category (auto-detected if not provided)
            tags: List of tags
            source: Where the link came from (email, web, etc.)
            priority: Priority level (0-5)

        Returns:
            The created DocumentEntry, or None if duplicate
        """
        if not self.document:
            raise ValueError("No document set. Use set_document() first.")

        # Parse the URL
        link_info = self.parse_url(url)

        # Auto-detect section and category if not provided
        if not section:
            section = self.suggest_section(link_info)
        if not category:
            category = self.suggest_category(link_info)

        # Create the entry
        entry = DocumentEntry(
            title=title,
            url=link_info.clean_url,
            summary=summary,
            category=category,
            tags=tags or [],
            source=source,
            priority=priority
        )

        # Add to document
        if self.document.add_entry(entry, section):
            return entry
        return None

    def add_link_from_text(
        self,
        text: str,
        default_section: str = "this_week"
    ) -> list[DocumentEntry]:
        """
        Extract and add all links from a block of text.

        Useful for processing emails or pasted content.

        Args:
            text: Text containing URLs
            default_section: Section to add links to

        Returns:
            List of created DocumentEntries
        """
        if not self.document:
            raise ValueError("No document set. Use set_document() first.")

        urls = self.extract_urls(text)
        entries = []

        for url in urls:
            link_info = self.parse_url(url)

            # Generate a basic title from the URL
            title = self._generate_title_from_url(url, link_info)

            entry = self.add_link(
                url=url,
                title=title,
                section=default_section,
                source="text_import"
            )

            if entry:
                entries.append(entry)

        return entries

    def _generate_title_from_url(self, url: str, link_info: LinkInfo) -> str:
        """Generate a basic title from URL when none is provided."""
        parsed = urlparse(url)

        # Try to extract a meaningful title from the path
        path_parts = [p for p in parsed.path.split("/") if p]

        if link_info.platform == "linkedin":
            if "posts" in path_parts:
                idx = path_parts.index("posts")
                if idx > 0:
                    return f"LinkedIn Post: {path_parts[idx-1].replace('-', ' ').title()}"
            return f"LinkedIn {link_info.content_type.replace('_', ' ').title()}"

        if link_info.platform == "twitter":
            if path_parts:
                return f"Tweet by @{path_parts[0]}"
            return "Twitter Post"

        if link_info.platform == "youtube":
            return "YouTube Video"

        if path_parts:
            # Use the last meaningful path segment as title
            title = path_parts[-1].replace("-", " ").replace("_", " ")
            # Remove file extensions
            title = re.sub(r'\.\w+$', '', title)
            return title.title()

        return f"Link from {link_info.domain}"

    def update_link(
        self,
        url: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[list] = None,
        priority: Optional[int] = None
    ) -> bool:
        """
        Update an existing link's properties.

        Args:
            url: URL of the entry to update
            title: New title (optional)
            summary: New summary (optional)
            status: New status (optional)
            tags: New tags (optional)
            priority: New priority (optional)

        Returns:
            True if updated successfully
        """
        if not self.document:
            raise ValueError("No document set. Use set_document() first.")

        entry = self.document.find_entry(url)
        if not entry:
            # Try with cleaned URL
            link_info = self.parse_url(url)
            entry = self.document.find_entry(link_info.clean_url)

        if not entry:
            return False

        if title is not None:
            entry.title = title
        if summary is not None:
            entry.summary = summary
        if status is not None:
            entry.status = status
        if tags is not None:
            entry.tags = tags
        if priority is not None:
            entry.priority = priority

        entry.update_modified()
        return True

    def get_links_needing_summary(self) -> list[DocumentEntry]:
        """Get all links that don't have summaries."""
        if not self.document:
            return []

        results = []
        for section in self.document.sections.values():
            for entry in section.entries:
                if not entry.summary:
                    results.append(entry)

        return results

    def get_duplicate_links(self) -> list[tuple[str, list[DocumentEntry]]]:
        """
        Find potential duplicate links (same domain + similar path).

        Returns:
            List of (domain, entries) tuples for potential duplicates
        """
        if not self.document:
            return []

        # Group by domain
        by_domain = {}
        for section in self.document.sections.values():
            for entry in section.entries:
                link_info = self.parse_url(entry.url)
                domain = link_info.domain
                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append(entry)

        # Return domains with multiple entries
        return [
            (domain, entries)
            for domain, entries in by_domain.items()
            if len(entries) > 1
        ]
