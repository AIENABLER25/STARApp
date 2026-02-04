"""
Document Watcher - Monitors documents for changes and triggers formatting.

Uses file system monitoring to detect changes and auto-apply rules.
"""

import hashlib
import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from .document import Document
from .format_engine import FormatEngine, FormatChange
from .rules import RulesConfig


@dataclass
class WatchEvent:
    """Record of a file change event."""
    path: str
    event_type: str  # created, modified, deleted
    timestamp: str
    changes_applied: list  # List of FormatChange if auto-format is enabled


class DocumentWatcher:
    """
    Watches documents for changes and auto-applies formatting.

    Features:
    - Monitor single file or directory
    - Detect content changes via hash comparison
    - Auto-apply formatting rules on change
    - Callback system for custom handlers
    - Event logging
    """

    def __init__(
        self,
        rules: Optional[RulesConfig] = None,
        auto_format: bool = True,
        auto_save: bool = True,
        check_interval: float = 2.0
    ):
        """
        Initialize the watcher.

        Args:
            rules: Rules configuration for formatting
            auto_format: Automatically apply formatting on changes
            auto_save: Automatically save after formatting
            check_interval: Seconds between file checks
        """
        self.rules = rules or RulesConfig()
        self.format_engine = FormatEngine(self.rules)
        self.auto_format = auto_format
        self.auto_save = auto_save
        self.check_interval = check_interval

        self._watched_files: dict[Path, str] = {}  # path -> hash
        self._running = False
        self._watch_thread: Optional[threading.Thread] = None
        self._callbacks: list[Callable[[WatchEvent], None]] = []
        self._event_log: list[WatchEvent] = []

    def add_callback(self, callback: Callable[[WatchEvent], None]):
        """Add a callback function to be called on file changes."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[WatchEvent], None]):
        """Remove a callback function."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _compute_hash(self, path: Path) -> str:
        """Compute MD5 hash of file contents."""
        try:
            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (IOError, OSError):
            return ""

    def watch_file(self, path: Path):
        """
        Add a file to the watch list.

        Args:
            path: Path to the document file
        """
        path = Path(path)
        if path.exists():
            self._watched_files[path] = self._compute_hash(path)

    def watch_directory(self, directory: Path, pattern: str = "*.json"):
        """
        Watch all matching files in a directory.

        Args:
            directory: Directory to watch
            pattern: Glob pattern for files to watch
        """
        directory = Path(directory)
        if directory.exists():
            for file_path in directory.glob(pattern):
                self.watch_file(file_path)

    def unwatch(self, path: Path):
        """Stop watching a file."""
        path = Path(path)
        if path in self._watched_files:
            del self._watched_files[path]

    def start(self):
        """Start watching for changes in a background thread."""
        if self._running:
            return

        self._running = True
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watch_thread.start()

    def stop(self):
        """Stop watching for changes."""
        self._running = False
        if self._watch_thread:
            self._watch_thread.join(timeout=5.0)
            self._watch_thread = None

    def _watch_loop(self):
        """Main watch loop running in background thread."""
        while self._running:
            self._check_files()
            time.sleep(self.check_interval)

    def _check_files(self):
        """Check all watched files for changes."""
        for path in list(self._watched_files.keys()):
            if not path.exists():
                # File was deleted
                event = WatchEvent(
                    path=str(path),
                    event_type="deleted",
                    timestamp=datetime.now().isoformat(),
                    changes_applied=[]
                )
                self._handle_event(event)
                del self._watched_files[path]
                continue

            current_hash = self._compute_hash(path)
            if current_hash != self._watched_files[path]:
                # File was modified
                self._watched_files[path] = current_hash

                changes = []
                if self.auto_format:
                    changes = self._apply_formatting(path)

                event = WatchEvent(
                    path=str(path),
                    event_type="modified",
                    timestamp=datetime.now().isoformat(),
                    changes_applied=changes
                )
                self._handle_event(event)

    def _apply_formatting(self, path: Path) -> list:
        """Apply formatting rules to a changed document."""
        try:
            document = Document.load(path)
            changes = self.format_engine.format_document(document)

            if changes and self.auto_save:
                document.save()
                # Update hash after save
                self._watched_files[path] = self._compute_hash(path)

            return [
                {
                    "entry_url": c.entry_url,
                    "change_type": c.change_type,
                    "old_value": c.old_value,
                    "new_value": c.new_value
                }
                for c in changes
            ]
        except Exception as e:
            print(f"Error formatting {path}: {e}")
            return []

    def _handle_event(self, event: WatchEvent):
        """Handle a file change event."""
        self._event_log.append(event)

        # Call registered callbacks
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Callback error: {e}")

    def check_now(self) -> list[WatchEvent]:
        """
        Manually trigger a check of all watched files.

        Returns:
            List of events detected
        """
        events_before = len(self._event_log)
        self._check_files()
        return self._event_log[events_before:]

    def get_event_log(self) -> list[WatchEvent]:
        """Get the log of all events."""
        return self._event_log.copy()

    def clear_event_log(self):
        """Clear the event log."""
        self._event_log = []

    def get_watched_files(self) -> list[Path]:
        """Get list of currently watched files."""
        return list(self._watched_files.keys())


class ChangeDetector:
    """
    Detects specific types of changes between document versions.

    Useful for understanding what changed in a document update.
    """

    @staticmethod
    def compare_documents(old_doc: Document, new_doc: Document) -> dict:
        """
        Compare two document versions and identify changes.

        Args:
            old_doc: Previous version of document
            new_doc: New version of document

        Returns:
            Dictionary describing changes
        """
        changes = {
            "added_entries": [],
            "removed_entries": [],
            "modified_entries": [],
            "section_changes": [],
            "metadata_changes": []
        }

        # Build URL maps for comparison
        old_entries = {}
        new_entries = {}

        for section in old_doc.sections.values():
            for entry in section.entries:
                old_entries[entry.url] = (entry, section.name)

        for section in new_doc.sections.values():
            for entry in section.entries:
                new_entries[entry.url] = (entry, section.name)

        # Find added entries
        for url, (entry, section) in new_entries.items():
            if url not in old_entries:
                changes["added_entries"].append({
                    "url": url,
                    "title": entry.title,
                    "section": section
                })

        # Find removed entries
        for url, (entry, section) in old_entries.items():
            if url not in new_entries:
                changes["removed_entries"].append({
                    "url": url,
                    "title": entry.title,
                    "section": section
                })

        # Find modified entries
        for url in set(old_entries.keys()) & set(new_entries.keys()):
            old_entry, old_section = old_entries[url]
            new_entry, new_section = new_entries[url]

            entry_changes = []

            if old_entry.title != new_entry.title:
                entry_changes.append({
                    "field": "title",
                    "old": old_entry.title,
                    "new": new_entry.title
                })

            if old_entry.summary != new_entry.summary:
                entry_changes.append({
                    "field": "summary",
                    "old": old_entry.summary,
                    "new": new_entry.summary
                })

            if old_entry.status != new_entry.status:
                entry_changes.append({
                    "field": "status",
                    "old": old_entry.status,
                    "new": new_entry.status
                })

            if old_entry.color != new_entry.color:
                entry_changes.append({
                    "field": "color",
                    "old": old_entry.color,
                    "new": new_entry.color
                })

            if set(old_entry.tags) != set(new_entry.tags):
                entry_changes.append({
                    "field": "tags",
                    "old": old_entry.tags,
                    "new": new_entry.tags
                })

            if old_section != new_section:
                changes["section_changes"].append({
                    "url": url,
                    "title": new_entry.title,
                    "old_section": old_section,
                    "new_section": new_section
                })

            if entry_changes:
                changes["modified_entries"].append({
                    "url": url,
                    "title": new_entry.title,
                    "changes": entry_changes
                })

        # Check metadata changes
        if old_doc.title != new_doc.title:
            changes["metadata_changes"].append({
                "field": "title",
                "old": old_doc.title,
                "new": new_doc.title
            })

        return changes

    @staticmethod
    def format_changes_report(changes: dict) -> str:
        """Format changes into a readable report."""
        lines = ["# Document Changes Report", ""]

        if changes["added_entries"]:
            lines.append(f"## Added ({len(changes['added_entries'])})")
            for entry in changes["added_entries"]:
                lines.append(f"- **{entry['title']}** (in {entry['section']})")
            lines.append("")

        if changes["removed_entries"]:
            lines.append(f"## Removed ({len(changes['removed_entries'])})")
            for entry in changes["removed_entries"]:
                lines.append(f"- ~~{entry['title']}~~ (was in {entry['section']})")
            lines.append("")

        if changes["modified_entries"]:
            lines.append(f"## Modified ({len(changes['modified_entries'])})")
            for entry in changes["modified_entries"]:
                lines.append(f"- **{entry['title']}**")
                for change in entry["changes"]:
                    lines.append(f"  - {change['field']}: `{change['old']}` → `{change['new']}`")
            lines.append("")

        if changes["section_changes"]:
            lines.append(f"## Moved ({len(changes['section_changes'])})")
            for entry in changes["section_changes"]:
                lines.append(f"- **{entry['title']}**: {entry['old_section']} → {entry['new_section']}")
            lines.append("")

        if not any([changes["added_entries"], changes["removed_entries"],
                   changes["modified_entries"], changes["section_changes"]]):
            lines.append("No changes detected.")

        return "\n".join(lines)
