#!/usr/bin/env python3
"""
Document Link Manager (DLM) - Main entry point.

A tool for managing hyperlinks in weekly CEO documents.
Captures links with summaries, enforces formatting rules, and monitors changes.

Usage:
    python dlm.py init --output my_document.json --title "Weekly Links"
    python dlm.py --document my_document.json add URL --title "Article Title" --summary "Brief summary"
    python dlm.py --document my_document.json list
    python dlm.py --document my_document.json format
    python dlm.py --document my_document.json export --format markdown --output weekly.md
"""

from document_link_manager.cli import main

if __name__ == "__main__":
    main()
