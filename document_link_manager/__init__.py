"""
Document Link Manager - A tool for managing hyperlinks in weekly CEO documents.

This tool helps manage documents with links by:
- Capturing and adding new links with summaries
- Enforcing formatting rules and colors
- Monitoring document changes
- Auto-formatting based on configurable rules
"""

__version__ = "1.0.0"
__author__ = "STARApp Team"

from .link_manager import LinkManager
from .document import Document, DocumentEntry
from .summarizer import ContentSummarizer
from .format_engine import FormatEngine
from .watcher import DocumentWatcher
from .rules import RulesConfig

__all__ = [
    "LinkManager",
    "Document",
    "DocumentEntry",
    "ContentSummarizer",
    "FormatEngine",
    "DocumentWatcher",
    "RulesConfig",
]
