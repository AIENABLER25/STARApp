# STARApp - Document Link Manager

A powerful tool for managing hyperlinks in weekly executive documents. Designed for CEOs and leaders who need to capture, organize, and maintain links to content from various sources like email, LinkedIn, articles, and more.

## Features

- **Web Interface**: Browser-based dashboard for easy link management
- **Link Management**: Add, update, remove, and organize hyperlinks with titles and summaries
- **Auto-Categorization**: Automatically detects platform (LinkedIn, Twitter, YouTube, etc.) and suggests categories
- **Formatting Rules Engine**: Configurable rules for colors, sections, and auto-tagging
- **Document Watching**: Monitor documents for changes and auto-apply formatting
- **Multiple Export Formats**: Export to Markdown, HTML, or JSON
- **URL Cleaning**: Automatically removes tracking parameters from URLs
- **Content Summarization**: Framework for summarizing linked content

## Web Interface (Recommended)

The easiest way to use the Document Link Manager is through the web interface:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python web_app.py
```

Then open **http://localhost:5000** in your browser.

### Web Interface Features

- **Dashboard**: View all your links organized by section
- **Quick Add**: Paste a URL to quickly add it with auto-detected title
- **Status Updates**: Change status with one click (New, In Progress, Completed, Archived)
- **Formatting**: Apply formatting rules with a single button
- **Export**: Download your document as Markdown, HTML, or JSON

![Dashboard Screenshot](docs/dashboard.png)

## CLI Quick Start

### 1. Initialize a New Document

```bash
python dlm.py init --output my_weekly.json --title "CEO Weekly Links"
```

### 2. Add a Link

```bash
python dlm.py --document my_weekly.json add \
    "https://www.linkedin.com/posts/example-post" \
    --title "Important Article about AI" \
    --summary "Key insights on AI-powered workflows" \
    --priority 3 \
    --tags ai productivity
```

### 3. List All Entries

```bash
python dlm.py --document my_weekly.json list
```

### 4. Apply Formatting Rules

```bash
python dlm.py --document my_weekly.json --rules config/default_rules.json format
```

### 5. Export to Markdown

```bash
python dlm.py --document my_weekly.json export --format markdown --output weekly.md
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Create a new document |
| `add` | Add a single link |
| `batch-add` | Add multiple links from text/file |
| `list` | List all entries |
| `search` | Search entries by keyword |
| `update` | Update an existing entry |
| `move` | Move entry to a different section |
| `remove` | Remove an entry |
| `format` | Apply formatting rules |
| `export` | Export document (markdown/html/json) |
| `watch` | Watch for changes and auto-format |
| `stats` | Show document statistics |
| `rules` | Manage formatting rules |
| `summarize` | Generate summary for a URL |

## Document Structure

Documents are organized into sections:

- **Priority**: High-priority items requiring immediate attention
- **This Week**: Current week's focus items
- **Action Items**: Tasks that need action
- **Reading List**: Articles and content to read
- **Follow Up**: Items requiring follow-up
- **References**: Reference materials and resources
- **Ideas**: Ideas and inspirations
- **Archive**: Completed or archived items

## Formatting Rules

The rules engine supports:

### Color Rules
Apply colors based on priority, status, or custom conditions:

```json
{
  "name": "high_priority_color",
  "conditions": [{"field": "priority", "match_type": "equals", "value": "3"}],
  "action": "color",
  "action_value": "#FF6B6B"
}
```

### Auto-Tagging
Automatically tag entries based on URL domain:

```json
{
  "name": "linkedin_tag",
  "conditions": [{"field": "url", "match_type": "domain", "value": "linkedin.com"}],
  "action": "add_tag",
  "action_value": "linkedin"
}
```

### Section Rules
Automatically move entries to appropriate sections:

```json
{
  "section_name": "priority",
  "conditions": [{"field": "priority", "match_type": "equals", "value": "3"}],
  "priority": 100
}
```

## Entry Properties

Each entry supports:

| Property | Description |
|----------|-------------|
| `title` | Display title for the link |
| `url` | The hyperlink URL |
| `summary` | Brief description of the content |
| `category` | reading, action_item, reference, meeting, research, follow_up, idea |
| `status` | new, in_progress, completed, archived |
| `tags` | List of tags for filtering |
| `priority` | 0-5 (0 = normal, 5 = critical) |
| `source` | Where the link came from (email, web, etc.) |
| `color` | Hex color code for display |

## Example Workflow

1. **Morning**: Check inbox for interesting articles
2. **Capture**: Add links with basic info
   ```bash
   python dlm.py -d weekly.json add "URL" -t "Title" -s "Quick summary"
   ```
3. **Organize**: Apply formatting rules
   ```bash
   python dlm.py -d weekly.json format
   ```
4. **Review**: Export for weekly review
   ```bash
   python dlm.py -d weekly.json export -f html -o weekly.html
   ```

## Watching for Changes

Enable auto-formatting when the document changes:

```bash
python dlm.py --document my_weekly.json watch --interval 5
```

This will:
- Monitor the file for changes
- Automatically apply formatting rules
- Log all changes made

## Python API Usage

```python
from document_link_manager import Document, LinkManager, FormatEngine, RulesConfig

# Create or load document
doc = Document(title="My Weekly Links")
# or: doc = Document.load("my_weekly.json")

# Add links
manager = LinkManager(doc)
manager.add_link(
    url="https://example.com/article",
    title="Interesting Article",
    summary="Key takeaways from this article",
    tags=["tech", "ai"],
    priority=2
)

# Apply formatting
rules = RulesConfig("config/default_rules.json")
engine = FormatEngine(rules)
changes = engine.format_document(doc)

# Save
doc.save("my_weekly.json")

# Export
doc.export_markdown("weekly.md")
```

## File Structure

```
STARApp/
├── web_app.py                  # Web application (Flask)
├── dlm.py                      # CLI entry point
├── document_link_manager/      # Core package
│   ├── __init__.py
│   ├── document.py            # Document model
│   ├── link_manager.py        # Link management
│   ├── summarizer.py          # Content summarization
│   ├── rules.py               # Rules configuration
│   ├── format_engine.py       # Formatting engine
│   ├── watcher.py             # File watching
│   └── cli.py                 # Command-line interface
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html             # Dashboard
│   ├── add_link.html          # Add link form
│   ├── edit_link.html         # Edit link form
│   └── rules.html             # Rules viewer
├── static/
│   ├── css/style.css          # Stylesheet
│   └── js/app.js              # JavaScript
├── config/
│   └── default_rules.json     # Default formatting rules
├── data/                       # Document storage
├── examples/
│   └── weekly_document.json   # Example document
├── requirements.txt           # Dependencies
└── README.md
```

## Color Scheme

Default colors used:

| Purpose | Color | Hex |
|---------|-------|-----|
| Priority (High) | Red | #FF6B6B |
| Priority (Urgent) | Bright Red | #FF0000 |
| New | Teal | #4ECDC4 |
| In Progress | Blue | #45B7D1 |
| Completed | Green | #96CEB4 |
| Archived | Gray | #95A5A6 |
| Follow Up | Yellow | #F7DC6F |
| Ideas | Purple | #BB8FCE |

## Requirements

- Python 3.9+
- No external dependencies for core functionality

Optional dependencies for enhanced features:
- `requests` - HTTP fetching for content summarization
- `beautifulsoup4` - HTML parsing
- `watchdog` - Advanced file watching
- `rich` - Enhanced terminal output

## License

MIT License
