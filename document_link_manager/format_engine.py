"""
Format Engine - Applies formatting rules to documents.

Ensures documents maintain consistent formatting, colors, and organization.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .document import Document, DocumentEntry, DocumentSection
from .rules import RulesConfig


@dataclass
class FormatChange:
    """Record of a formatting change made."""
    entry_url: str
    entry_title: str
    change_type: str  # color, section, tag, style
    old_value: str
    new_value: str
    rule_name: str
    timestamp: str


class FormatEngine:
    """
    Applies formatting rules to documents.

    Features:
    - Apply color rules based on status, category, priority
    - Move entries to correct sections
    - Add auto-tags
    - Validate entries
    - Track changes for review
    """

    def __init__(self, rules: Optional[RulesConfig] = None):
        """
        Initialize the format engine.

        Args:
            rules: Rules configuration (uses defaults if not provided)
        """
        self.rules = rules or RulesConfig()
        self.change_history: list[FormatChange] = []

    def set_rules(self, rules: RulesConfig):
        """Set the rules configuration."""
        self.rules = rules

    def format_document(
        self,
        document: Document,
        dry_run: bool = False
    ) -> list[FormatChange]:
        """
        Apply all formatting rules to a document.

        Args:
            document: The document to format
            dry_run: If True, report changes without applying them

        Returns:
            List of changes made (or would be made in dry_run)
        """
        changes = []

        # Process each entry
        for section_key, section in document.sections.items():
            for entry in section.entries[:]:  # Copy list to allow modifications
                entry_changes = self._format_entry(
                    document, entry, section_key, dry_run
                )
                changes.extend(entry_changes)

        # Sort sections according to rules
        if not dry_run:
            self._sort_sections(document)

        # Record changes
        if not dry_run:
            self.change_history.extend(changes)

        return changes

    def _format_entry(
        self,
        document: Document,
        entry: DocumentEntry,
        current_section: str,
        dry_run: bool
    ) -> list[FormatChange]:
        """Format a single entry."""
        changes = []
        entry_data = entry.to_dict()

        # Apply color
        new_color = self.rules.get_color_for_entry(entry_data)
        if new_color and new_color != entry.color:
            changes.append(FormatChange(
                entry_url=entry.url,
                entry_title=entry.title,
                change_type="color",
                old_value=entry.color or "(none)",
                new_value=new_color,
                rule_name="color_rule",
                timestamp=datetime.now().isoformat()
            ))
            if not dry_run:
                entry.color = new_color
                entry.update_modified()

        # Check section assignment
        suggested_section = self.rules.get_section_for_entry(entry_data)
        if suggested_section and suggested_section != current_section:
            changes.append(FormatChange(
                entry_url=entry.url,
                entry_title=entry.title,
                change_type="section",
                old_value=current_section,
                new_value=suggested_section,
                rule_name="section_rule",
                timestamp=datetime.now().isoformat()
            ))
            if not dry_run:
                document.move_entry(entry.url, suggested_section)

        # Apply auto-tags
        auto_tags = self.rules.get_auto_tags(entry_data)
        new_tags = [t for t in auto_tags if t not in entry.tags]
        if new_tags:
            changes.append(FormatChange(
                entry_url=entry.url,
                entry_title=entry.title,
                change_type="tag",
                old_value=",".join(entry.tags),
                new_value=",".join(entry.tags + new_tags),
                rule_name="auto_tag_rule",
                timestamp=datetime.now().isoformat()
            ))
            if not dry_run:
                entry.tags.extend(new_tags)
                entry.update_modified()

        return changes

    def _sort_sections(self, document: Document):
        """Sort sections according to configured order."""
        order_map = {
            name: i for i, name in enumerate(self.rules.section_order)
        }

        for section_key, section in document.sections.items():
            # Get order from config, default to end
            section.sort_order = order_map.get(section_key, 999)

    def validate_document(self, document: Document) -> dict[str, list[str]]:
        """
        Validate all entries in a document.

        Args:
            document: The document to validate

        Returns:
            Dict mapping entry URLs to lists of validation errors
        """
        validation_results = {}

        for section in document.sections.values():
            for entry in section.entries:
                errors = self.rules.validate_entry(entry.to_dict())
                if errors:
                    validation_results[entry.url] = errors

        return validation_results

    def format_single_entry(
        self,
        entry: DocumentEntry,
        apply_changes: bool = True
    ) -> list[FormatChange]:
        """
        Apply formatting to a single entry without document context.

        Args:
            entry: The entry to format
            apply_changes: Whether to apply changes to the entry

        Returns:
            List of changes made
        """
        changes = []
        entry_data = entry.to_dict()

        # Apply color
        new_color = self.rules.get_color_for_entry(entry_data)
        if new_color and new_color != entry.color:
            changes.append(FormatChange(
                entry_url=entry.url,
                entry_title=entry.title,
                change_type="color",
                old_value=entry.color or "(none)",
                new_value=new_color,
                rule_name="color_rule",
                timestamp=datetime.now().isoformat()
            ))
            if apply_changes:
                entry.color = new_color
                entry.update_modified()

        # Apply auto-tags
        auto_tags = self.rules.get_auto_tags(entry_data)
        new_tags = [t for t in auto_tags if t not in entry.tags]
        if new_tags:
            changes.append(FormatChange(
                entry_url=entry.url,
                entry_title=entry.title,
                change_type="tag",
                old_value=",".join(entry.tags),
                new_value=",".join(entry.tags + new_tags),
                rule_name="auto_tag_rule",
                timestamp=datetime.now().isoformat()
            ))
            if apply_changes:
                entry.tags.extend(new_tags)
                entry.update_modified()

        return changes

    def get_change_report(self, changes: list[FormatChange]) -> str:
        """
        Generate a human-readable report of changes.

        Args:
            changes: List of format changes

        Returns:
            Formatted report string
        """
        if not changes:
            return "No formatting changes needed."

        lines = ["# Formatting Changes Report", ""]

        # Group by change type
        by_type = {}
        for change in changes:
            if change.change_type not in by_type:
                by_type[change.change_type] = []
            by_type[change.change_type].append(change)

        for change_type, type_changes in by_type.items():
            lines.append(f"## {change_type.title()} Changes ({len(type_changes)})")
            lines.append("")

            for change in type_changes:
                lines.append(f"- **{change.entry_title}**")
                lines.append(f"  - Changed: `{change.old_value}` → `{change.new_value}`")
                lines.append(f"  - Rule: {change.rule_name}")
                lines.append("")

        return "\n".join(lines)

    def export_change_history(self, path: Path):
        """Export change history to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = [
            {
                "entry_url": c.entry_url,
                "entry_title": c.entry_title,
                "change_type": c.change_type,
                "old_value": c.old_value,
                "new_value": c.new_value,
                "rule_name": c.rule_name,
                "timestamp": c.timestamp
            }
            for c in self.change_history
        ]

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def clear_change_history(self):
        """Clear the change history."""
        self.change_history = []


class StyleFormatter:
    """
    Handles visual styling for different output formats.

    Supports:
    - Markdown with color hints
    - HTML with inline styles
    - Plain text
    """

    # ANSI color codes for terminal output
    ANSI_COLORS = {
        "#FF6B6B": "\033[91m",  # Red
        "#FF0000": "\033[91m",  # Bright Red
        "#4ECDC4": "\033[96m",  # Cyan
        "#45B7D1": "\033[94m",  # Blue
        "#96CEB4": "\033[92m",  # Green
        "#95A5A6": "\033[90m",  # Gray
        "#F7DC6F": "\033[93m",  # Yellow
        "#FFA500": "\033[33m",  # Orange
        "#DDA0DD": "\033[95m",  # Magenta
        "#BB8FCE": "\033[35m",  # Purple
    }
    ANSI_RESET = "\033[0m"

    @classmethod
    def to_colored_terminal(cls, text: str, color: str) -> str:
        """Add ANSI color codes for terminal output."""
        ansi = cls.ANSI_COLORS.get(color, "")
        if ansi:
            return f"{ansi}{text}{cls.ANSI_RESET}"
        return text

    @classmethod
    def to_html_styled(cls, text: str, color: str) -> str:
        """Add inline HTML style for color."""
        if color:
            return f'<span style="color: {color}">{text}</span>'
        return text

    @classmethod
    def entry_to_html(cls, entry: DocumentEntry) -> str:
        """Convert entry to styled HTML."""
        color = entry.color or "#000000"

        html_parts = [
            f'<li style="color: {color}">',
            f'  <a href="{entry.url}" style="color: {color}">{entry.title}</a>'
        ]

        if entry.summary:
            html_parts.append(f'  <span class="summary"> - {entry.summary}</span>')

        if entry.tags:
            tags_html = " ".join(f'<span class="tag">#{t}</span>' for t in entry.tags)
            html_parts.append(f'  <div class="tags">{tags_html}</div>')

        html_parts.append('</li>')

        return "\n".join(html_parts)

    @classmethod
    def entry_to_markdown_with_color(cls, entry: DocumentEntry) -> str:
        """
        Convert entry to markdown with color comment hints.

        Since markdown doesn't support colors natively, we add HTML comments
        that tools like Obsidian or custom renderers can use.
        """
        color_hint = f"<!-- color: {entry.color} -->" if entry.color else ""

        line = f"- [{entry.title}]({entry.url})"
        if entry.summary:
            line += f" - {entry.summary}"

        if entry.tags:
            line += f" `{' '.join('#' + t for t in entry.tags)}`"

        return f"{color_hint}\n{line}" if color_hint else line

    @classmethod
    def document_to_html(cls, document: Document) -> str:
        """Export entire document to styled HTML."""
        lines = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            f'  <title>{document.title}</title>',
            '  <style>',
            '    body { font-family: -apple-system, system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }',
            '    h1 { color: #333; }',
            '    h2 { color: #666; border-bottom: 1px solid #eee; padding-bottom: 5px; }',
            '    ul { list-style: none; padding-left: 0; }',
            '    li { margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; }',
            '    a { text-decoration: none; font-weight: 500; }',
            '    a:hover { text-decoration: underline; }',
            '    .summary { color: #666; }',
            '    .tags { margin-top: 5px; }',
            '    .tag { background: #e0e0e0; padding: 2px 8px; border-radius: 3px; font-size: 12px; margin-right: 5px; }',
            '    .meta { color: #999; font-size: 12px; margin-bottom: 20px; }',
            '  </style>',
            '</head>',
            '<body>',
            f'  <h1>{document.title}</h1>',
            f'  <p class="meta">Last updated: {document.metadata["modified"][:10]}</p>',
        ]

        # Sort sections
        sorted_sections = sorted(
            document.sections.values(),
            key=lambda s: s.sort_order
        )

        for section in sorted_sections:
            if not section.entries:
                continue

            section_color = section.color or "#666"
            lines.append(f'  <h2 style="color: {section_color}">{section.name}</h2>')
            lines.append('  <ul>')

            for entry in section.entries:
                lines.append(cls.entry_to_html(entry))

            lines.append('  </ul>')

        lines.extend([
            '</body>',
            '</html>'
        ])

        return "\n".join(lines)
