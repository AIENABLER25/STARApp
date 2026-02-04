"""
Document model for managing the CEO's weekly document with links.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class EntryStatus(Enum):
    """Status of a document entry."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    PRIORITY = "priority"


class EntryCategory(Enum):
    """Category types for document entries."""
    READING = "reading"
    ACTION_ITEM = "action_item"
    REFERENCE = "reference"
    MEETING = "meeting"
    RESEARCH = "research"
    FOLLOW_UP = "follow_up"
    IDEA = "idea"
    OTHER = "other"


@dataclass
class DocumentEntry:
    """
    Represents a single entry in the document with a hyperlink.
    """
    title: str
    url: str
    summary: str = ""
    category: str = "other"
    status: str = "new"
    tags: list = field(default_factory=list)
    notes: str = ""
    source: str = ""  # Where the link came from (email, web, meeting, etc.)
    date_added: str = field(default_factory=lambda: datetime.now().isoformat())
    date_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 0  # 0 = normal, 1-5 = priority levels
    color: str = ""  # Color code for formatting

    def __post_init__(self):
        """Validate and normalize entry data."""
        # Normalize category
        try:
            self.category = EntryCategory(self.category.lower()).value
        except ValueError:
            self.category = EntryCategory.OTHER.value

        # Normalize status
        try:
            self.status = EntryStatus(self.status.lower()).value
        except ValueError:
            self.status = EntryStatus.NEW.value

    def to_dict(self) -> dict:
        """Convert entry to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentEntry":
        """Create entry from dictionary."""
        return cls(**data)

    def to_markdown(self, include_metadata: bool = True) -> str:
        """
        Convert entry to markdown format with hyperlink.

        Format: - [Title](URL) - Summary
        """
        # Build the main link line
        line = f"- [{self.title}]({self.url})"

        if self.summary:
            line += f" - {self.summary}"

        if include_metadata:
            metadata_parts = []
            if self.tags:
                metadata_parts.append(f"Tags: {', '.join(self.tags)}")
            if self.status != "new":
                metadata_parts.append(f"Status: {self.status}")
            if self.priority > 0:
                metadata_parts.append(f"Priority: {'!' * self.priority}")

            if metadata_parts:
                line += f"\n  *{' | '.join(metadata_parts)}*"

        return line

    def update_modified(self):
        """Update the modified timestamp."""
        self.date_modified = datetime.now().isoformat()


@dataclass
class DocumentSection:
    """A section within the document containing related entries."""
    name: str
    entries: list = field(default_factory=list)
    color: str = ""
    sort_order: int = 0

    def add_entry(self, entry: DocumentEntry):
        """Add an entry to this section."""
        self.entries.append(entry)

    def remove_entry(self, url: str) -> bool:
        """Remove an entry by URL."""
        for i, entry in enumerate(self.entries):
            if entry.url == url:
                self.entries.pop(i)
                return True
        return False

    def to_dict(self) -> dict:
        """Convert section to dictionary."""
        return {
            "name": self.name,
            "entries": [e.to_dict() for e in self.entries],
            "color": self.color,
            "sort_order": self.sort_order
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentSection":
        """Create section from dictionary."""
        entries = [DocumentEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(
            name=data["name"],
            entries=entries,
            color=data.get("color", ""),
            sort_order=data.get("sort_order", 0)
        )


class Document:
    """
    Main document class for managing the CEO's weekly document.

    Supports both JSON storage and Markdown export.
    """

    def __init__(self, title: str = "Weekly Document", path: Optional[Path] = None):
        self.title = title
        self.path = path
        self.sections: dict[str, DocumentSection] = {}
        self.metadata = {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "version": "1.0"
        }
        self._init_default_sections()

    def _init_default_sections(self):
        """Initialize default document sections."""
        default_sections = [
            ("Priority", "#FF6B6B", 0),
            ("This Week", "#4ECDC4", 1),
            ("Reading List", "#45B7D1", 2),
            ("Action Items", "#96CEB4", 3),
            ("References", "#DDA0DD", 4),
            ("Follow Up", "#F7DC6F", 5),
            ("Ideas", "#BB8FCE", 6),
            ("Archive", "#95A5A6", 7),
        ]

        for name, color, order in default_sections:
            self.sections[name.lower().replace(" ", "_")] = DocumentSection(
                name=name, color=color, sort_order=order
            )

    def add_entry(self, entry: DocumentEntry, section: str = "reading_list") -> bool:
        """
        Add an entry to the specified section.

        Args:
            entry: The DocumentEntry to add
            section: Section key (e.g., 'reading_list', 'this_week')

        Returns:
            True if added successfully
        """
        section_key = section.lower().replace(" ", "_")

        if section_key not in self.sections:
            # Create new section if it doesn't exist
            self.sections[section_key] = DocumentSection(
                name=section.replace("_", " ").title(),
                sort_order=len(self.sections)
            )

        # Check for duplicate URLs
        for sec in self.sections.values():
            for existing in sec.entries:
                if existing.url == entry.url:
                    return False  # Duplicate found

        self.sections[section_key].add_entry(entry)
        self._update_modified()
        return True

    def remove_entry(self, url: str) -> bool:
        """Remove an entry by URL from any section."""
        for section in self.sections.values():
            if section.remove_entry(url):
                self._update_modified()
                return True
        return False

    def move_entry(self, url: str, to_section: str) -> bool:
        """Move an entry from one section to another."""
        entry_to_move = None

        # Find and remove the entry
        for section in self.sections.values():
            for entry in section.entries:
                if entry.url == url:
                    entry_to_move = entry
                    section.remove_entry(url)
                    break
            if entry_to_move:
                break

        if entry_to_move:
            return self.add_entry(entry_to_move, to_section)
        return False

    def find_entry(self, url: str) -> Optional[DocumentEntry]:
        """Find an entry by URL."""
        for section in self.sections.values():
            for entry in section.entries:
                if entry.url == url:
                    return entry
        return None

    def search_entries(self, query: str) -> list[DocumentEntry]:
        """Search entries by title, summary, or tags."""
        query = query.lower()
        results = []

        for section in self.sections.values():
            for entry in section.entries:
                if (query in entry.title.lower() or
                    query in entry.summary.lower() or
                    any(query in tag.lower() for tag in entry.tags)):
                    results.append(entry)

        return results

    def get_entries_by_status(self, status: str) -> list[DocumentEntry]:
        """Get all entries with a specific status."""
        results = []
        for section in self.sections.values():
            for entry in section.entries:
                if entry.status == status:
                    results.append(entry)
        return results

    def get_entries_by_category(self, category: str) -> list[DocumentEntry]:
        """Get all entries with a specific category."""
        results = []
        for section in self.sections.values():
            for entry in section.entries:
                if entry.category == category:
                    results.append(entry)
        return results

    def _update_modified(self):
        """Update the document modified timestamp."""
        self.metadata["modified"] = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert document to dictionary for JSON storage."""
        return {
            "title": self.title,
            "metadata": self.metadata,
            "sections": {k: v.to_dict() for k, v in self.sections.items()}
        }

    @classmethod
    def from_dict(cls, data: dict, path: Optional[Path] = None) -> "Document":
        """Create document from dictionary."""
        doc = cls(title=data.get("title", "Weekly Document"), path=path)
        doc.metadata = data.get("metadata", doc.metadata)
        doc.sections = {}

        for key, section_data in data.get("sections", {}).items():
            doc.sections[key] = DocumentSection.from_dict(section_data)

        return doc

    def save(self, path: Optional[Path] = None):
        """Save document to JSON file."""
        save_path = path or self.path
        if not save_path:
            raise ValueError("No path specified for saving")

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        self.path = save_path

    @classmethod
    def load(cls, path: Path) -> "Document":
        """Load document from JSON file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls.from_dict(data, path)

    def to_markdown(self, include_metadata: bool = True) -> str:
        """
        Export document to markdown format.

        This creates a nicely formatted markdown document with all links.
        """
        lines = [f"# {self.title}", ""]

        if include_metadata:
            lines.append(f"*Last updated: {self.metadata['modified'][:10]}*")
            lines.append("")

        # Sort sections by order
        sorted_sections = sorted(
            self.sections.values(),
            key=lambda s: s.sort_order
        )

        for section in sorted_sections:
            if not section.entries:
                continue

            lines.append(f"## {section.name}")
            lines.append("")

            for entry in section.entries:
                lines.append(entry.to_markdown(include_metadata))

            lines.append("")

        return "\n".join(lines)

    def export_markdown(self, path: Path):
        """Export document to a markdown file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_markdown())

    def get_stats(self) -> dict:
        """Get document statistics."""
        total_entries = sum(len(s.entries) for s in self.sections.values())
        entries_by_status = {}
        entries_by_category = {}

        for section in self.sections.values():
            for entry in section.entries:
                entries_by_status[entry.status] = entries_by_status.get(entry.status, 0) + 1
                entries_by_category[entry.category] = entries_by_category.get(entry.category, 0) + 1

        return {
            "total_entries": total_entries,
            "sections": len(self.sections),
            "by_status": entries_by_status,
            "by_category": entries_by_category
        }
