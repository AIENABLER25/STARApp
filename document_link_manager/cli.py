"""
CLI Interface - Command-line interface for the Document Link Manager.

Provides commands for managing documents, adding links, and applying formatting.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .document import Document, DocumentEntry
from .link_manager import LinkManager
from .summarizer import ContentSummarizer, ManualSummaryHelper
from .format_engine import FormatEngine, StyleFormatter
from .rules import RulesConfig
from .watcher import DocumentWatcher


class CLI:
    """Command-line interface for Document Link Manager."""

    def __init__(self):
        self.parser = self._create_parser()
        self.document: Optional[Document] = None
        self.link_manager: Optional[LinkManager] = None
        self.rules: Optional[RulesConfig] = None

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            prog="dlm",
            description="Document Link Manager - Manage hyperlinks in your weekly document"
        )
        parser.add_argument(
            "--document", "-d",
            type=str,
            help="Path to the document file (JSON format)"
        )
        parser.add_argument(
            "--rules", "-r",
            type=str,
            help="Path to the rules configuration file"
        )

        subparsers = parser.add_subparsers(dest="command", help="Commands")

        # Init command
        init_parser = subparsers.add_parser("init", help="Initialize a new document")
        init_parser.add_argument("--title", "-t", default="Weekly Document", help="Document title")
        init_parser.add_argument("--output", "-o", required=True, help="Output file path")

        # Add link command
        add_parser = subparsers.add_parser("add", help="Add a new link to the document")
        add_parser.add_argument("url", help="URL to add")
        add_parser.add_argument("--title", "-t", required=True, help="Title for the link")
        add_parser.add_argument("--summary", "-s", default="", help="Summary of the content")
        add_parser.add_argument("--section", default="this_week", help="Section to add to")
        add_parser.add_argument("--category", "-c", help="Category (reading, action_item, etc.)")
        add_parser.add_argument("--tags", nargs="+", default=[], help="Tags for the entry")
        add_parser.add_argument("--priority", "-p", type=int, default=0, help="Priority (0-5)")
        add_parser.add_argument("--source", default="", help="Source of the link (email, web, etc.)")

        # Batch add command
        batch_parser = subparsers.add_parser("batch-add", help="Add multiple links from text")
        batch_parser.add_argument("--file", "-f", help="File containing URLs/text")
        batch_parser.add_argument("--section", default="this_week", help="Section to add to")

        # List command
        list_parser = subparsers.add_parser("list", help="List entries in the document")
        list_parser.add_argument("--section", "-s", help="Filter by section")
        list_parser.add_argument("--status", help="Filter by status")
        list_parser.add_argument("--category", "-c", help="Filter by category")
        list_parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")

        # Search command
        search_parser = subparsers.add_parser("search", help="Search entries")
        search_parser.add_argument("query", help="Search query")

        # Update command
        update_parser = subparsers.add_parser("update", help="Update an entry")
        update_parser.add_argument("url", help="URL of entry to update")
        update_parser.add_argument("--title", "-t", help="New title")
        update_parser.add_argument("--summary", "-s", help="New summary")
        update_parser.add_argument("--status", help="New status")
        update_parser.add_argument("--tags", nargs="+", help="New tags")
        update_parser.add_argument("--priority", "-p", type=int, help="New priority")

        # Move command
        move_parser = subparsers.add_parser("move", help="Move entry to different section")
        move_parser.add_argument("url", help="URL of entry to move")
        move_parser.add_argument("section", help="Target section")

        # Remove command
        remove_parser = subparsers.add_parser("remove", help="Remove an entry")
        remove_parser.add_argument("url", help="URL of entry to remove")

        # Format command
        format_parser = subparsers.add_parser("format", help="Apply formatting rules")
        format_parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")

        # Export command
        export_parser = subparsers.add_parser("export", help="Export document")
        export_parser.add_argument("--format", "-f", choices=["markdown", "html", "json"], default="markdown")
        export_parser.add_argument("--output", "-o", required=True, help="Output file path")

        # Watch command
        watch_parser = subparsers.add_parser("watch", help="Watch document for changes")
        watch_parser.add_argument("--interval", "-i", type=float, default=2.0, help="Check interval in seconds")
        watch_parser.add_argument("--no-format", action="store_true", help="Don't auto-format on changes")

        # Stats command
        subparsers.add_parser("stats", help="Show document statistics")

        # Rules commands
        rules_parser = subparsers.add_parser("rules", help="Manage formatting rules")
        rules_sub = rules_parser.add_subparsers(dest="rules_command")

        rules_sub.add_parser("list", help="List current rules")
        rules_sub.add_parser("template", help="Generate a rules template")

        rules_init = rules_sub.add_parser("init", help="Initialize rules file")
        rules_init.add_argument("--output", "-o", required=True, help="Output file path")

        # Summarize command
        summarize_parser = subparsers.add_parser("summarize", help="Summarize a URL")
        summarize_parser.add_argument("url", help="URL to summarize")
        summarize_parser.add_argument("--update", "-u", action="store_true",
                                     help="Update entry summary if exists")

        return parser

    def run(self, args: Optional[list] = None):
        """Run the CLI with given arguments."""
        parsed = self.parser.parse_args(args)

        if not parsed.command:
            self.parser.print_help()
            return

        # Load document if specified
        if parsed.document:
            self._load_document(parsed.document)

        # Load rules if specified
        if hasattr(parsed, 'rules') and parsed.rules:
            self._load_rules(parsed.rules)

        # Dispatch to command handler
        command_handlers = {
            "init": self._cmd_init,
            "add": self._cmd_add,
            "batch-add": self._cmd_batch_add,
            "list": self._cmd_list,
            "search": self._cmd_search,
            "update": self._cmd_update,
            "move": self._cmd_move,
            "remove": self._cmd_remove,
            "format": self._cmd_format,
            "export": self._cmd_export,
            "watch": self._cmd_watch,
            "stats": self._cmd_stats,
            "rules": self._cmd_rules,
            "summarize": self._cmd_summarize,
        }

        handler = command_handlers.get(parsed.command)
        if handler:
            handler(parsed)
        else:
            print(f"Unknown command: {parsed.command}")

    def _load_document(self, path: str):
        """Load a document from file."""
        try:
            self.document = Document.load(Path(path))
            self.link_manager = LinkManager(self.document)
            print(f"Loaded document: {self.document.title}")
        except FileNotFoundError:
            print(f"Document not found: {path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading document: {e}")
            sys.exit(1)

    def _load_rules(self, path: str):
        """Load rules from file."""
        try:
            self.rules = RulesConfig(Path(path))
            print(f"Loaded rules from: {path}")
        except Exception as e:
            print(f"Error loading rules: {e}")
            self.rules = RulesConfig()

    def _ensure_document(self):
        """Ensure a document is loaded."""
        if not self.document:
            print("Error: No document specified. Use --document or init command.")
            sys.exit(1)

    def _cmd_init(self, args):
        """Initialize a new document."""
        doc = Document(title=args.title)
        output_path = Path(args.output)

        doc.save(output_path)
        print(f"Created new document: {output_path}")
        print(f"Title: {args.title}")
        print(f"Sections: {', '.join(doc.sections.keys())}")

    def _cmd_add(self, args):
        """Add a new link."""
        self._ensure_document()

        entry = self.link_manager.add_link(
            url=args.url,
            title=args.title,
            summary=args.summary,
            section=args.section,
            category=args.category,
            tags=args.tags,
            priority=args.priority,
            source=args.source
        )

        if entry:
            self.document.save()
            print(f"Added: [{entry.title}]({entry.url})")
            print(f"Section: {args.section}")
            if entry.tags:
                print(f"Tags: {', '.join(entry.tags)}")
        else:
            print("Failed to add link (may be duplicate)")

    def _cmd_batch_add(self, args):
        """Add multiple links from text or file."""
        self._ensure_document()

        if args.file:
            with open(args.file, 'r') as f:
                text = f.read()
        else:
            print("Enter text containing URLs (Ctrl+D to finish):")
            text = sys.stdin.read()

        entries = self.link_manager.add_link_from_text(text, args.section)

        if entries:
            self.document.save()
            print(f"Added {len(entries)} links:")
            for entry in entries:
                print(f"  - {entry.title}")
        else:
            print("No new links found to add")

    def _cmd_list(self, args):
        """List entries."""
        self._ensure_document()

        entries = []
        for section_key, section in self.document.sections.items():
            if args.section and section_key != args.section:
                continue

            for entry in section.entries:
                if args.status and entry.status != args.status:
                    continue
                if args.category and entry.category != args.category:
                    continue
                entries.append((section.name, entry))

        if args.format == "json":
            output = [{"section": s, **e.to_dict()} for s, e in entries]
            print(json.dumps(output, indent=2))
        elif args.format == "markdown":
            current_section = None
            for section, entry in entries:
                if section != current_section:
                    print(f"\n## {section}")
                    current_section = section
                print(entry.to_markdown())
        else:
            current_section = None
            for section, entry in entries:
                if section != current_section:
                    print(f"\n=== {section} ===")
                    current_section = section

                status_indicator = {
                    "new": "[ ]",
                    "in_progress": "[~]",
                    "completed": "[x]",
                    "archived": "[-]"
                }.get(entry.status, "[ ]")

                priority_str = "!" * entry.priority if entry.priority else ""
                print(f"{status_indicator} {priority_str}{entry.title}")
                print(f"    {entry.url}")
                if entry.summary:
                    print(f"    {entry.summary[:80]}...")

        print(f"\nTotal: {len(entries)} entries")

    def _cmd_search(self, args):
        """Search entries."""
        self._ensure_document()

        results = self.document.search_entries(args.query)

        if results:
            print(f"Found {len(results)} matching entries:\n")
            for entry in results:
                print(f"- {entry.title}")
                print(f"  {entry.url}")
                if entry.summary:
                    print(f"  {entry.summary[:80]}...")
                print()
        else:
            print("No matching entries found")

    def _cmd_update(self, args):
        """Update an entry."""
        self._ensure_document()

        updated = self.link_manager.update_link(
            url=args.url,
            title=args.title,
            summary=args.summary,
            status=args.status,
            tags=args.tags,
            priority=args.priority
        )

        if updated:
            self.document.save()
            print(f"Updated entry: {args.url}")
        else:
            print(f"Entry not found: {args.url}")

    def _cmd_move(self, args):
        """Move entry to different section."""
        self._ensure_document()

        if self.document.move_entry(args.url, args.section):
            self.document.save()
            print(f"Moved to section: {args.section}")
        else:
            print(f"Entry not found: {args.url}")

    def _cmd_remove(self, args):
        """Remove an entry."""
        self._ensure_document()

        if self.document.remove_entry(args.url):
            self.document.save()
            print(f"Removed entry: {args.url}")
        else:
            print(f"Entry not found: {args.url}")

    def _cmd_format(self, args):
        """Apply formatting rules."""
        self._ensure_document()

        rules = self.rules or RulesConfig()
        engine = FormatEngine(rules)

        changes = engine.format_document(self.document, dry_run=args.dry_run)

        if changes:
            print(engine.get_change_report(changes))
            if not args.dry_run:
                self.document.save()
                print("\nChanges applied and saved.")
        else:
            print("No formatting changes needed.")

    def _cmd_export(self, args):
        """Export document."""
        self._ensure_document()

        output_path = Path(args.output)

        if args.format == "markdown":
            self.document.export_markdown(output_path)
        elif args.format == "html":
            html = StyleFormatter.document_to_html(self.document)
            with open(output_path, 'w') as f:
                f.write(html)
        elif args.format == "json":
            with open(output_path, 'w') as f:
                json.dump(self.document.to_dict(), f, indent=2)

        print(f"Exported to: {output_path}")

    def _cmd_watch(self, args):
        """Watch document for changes."""
        self._ensure_document()

        rules = self.rules or RulesConfig()
        watcher = DocumentWatcher(
            rules=rules,
            auto_format=not args.no_format,
            check_interval=args.interval
        )

        watcher.watch_file(self.document.path)

        def on_change(event):
            print(f"[{event.timestamp}] {event.event_type}: {event.path}")
            if event.changes_applied:
                for change in event.changes_applied:
                    print(f"  - {change['change_type']}: {change['entry_url'][:50]}...")

        watcher.add_callback(on_change)

        print(f"Watching: {self.document.path}")
        print("Press Ctrl+C to stop...")

        try:
            watcher.start()
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop()
            print("\nStopped watching.")

    def _cmd_stats(self, args):
        """Show document statistics."""
        self._ensure_document()

        stats = self.document.get_stats()

        print(f"Document: {self.document.title}")
        print(f"Total Entries: {stats['total_entries']}")
        print(f"Sections: {stats['sections']}")

        if stats['by_status']:
            print("\nBy Status:")
            for status, count in stats['by_status'].items():
                print(f"  {status}: {count}")

        if stats['by_category']:
            print("\nBy Category:")
            for category, count in stats['by_category'].items():
                print(f"  {category}: {count}")

    def _cmd_rules(self, args):
        """Manage rules."""
        if args.rules_command == "list":
            rules = self.rules or RulesConfig()
            print("Formatting Rules:")
            for rule in rules.formatting_rules:
                status = "enabled" if rule.enabled else "disabled"
                print(f"  - {rule.name} ({status})")
                print(f"    {rule.description}")

        elif args.rules_command == "template":
            rules = RulesConfig()
            template = rules.create_template()
            print(json.dumps(template, indent=2))

        elif args.rules_command == "init":
            rules = RulesConfig()
            rules.save(Path(args.output))
            print(f"Created rules file: {args.output}")

        else:
            print("Use: rules list, rules template, or rules init")

    def _cmd_summarize(self, args):
        """Summarize a URL."""
        summarizer = ContentSummarizer()

        print(f"Summarizing: {args.url}")
        print("Note: Full summarization requires external HTTP library.")
        print("Using basic summarization...")

        title, summary = summarizer.summarize_url(args.url)
        print(f"\nTitle: {title}")
        print(f"Summary: {summary}")

        # If document is loaded and update flag is set
        if args.update and self.document:
            entry = self.document.find_entry(args.url)
            if entry:
                entry.summary = summary
                entry.update_modified()
                self.document.save()
                print("\nUpdated entry summary in document.")


def main():
    """Main entry point."""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
