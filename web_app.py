"""
Web Application - Flask-based web interface for Document Link Manager.

Provides a browser-accessible interface for managing the CEO's weekly document.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

# Import our document link manager modules
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_link_manager import (
    Document, DocumentEntry, LinkManager,
    FormatEngine, RulesConfig, ContentSummarizer
)

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.secret_key = 'star-app-secret-key-change-in-production'

# Configuration
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
DOCUMENT_PATH = DATA_DIR / 'weekly_document.json'
RULES_PATH = Path(__file__).parent / 'config' / 'default_rules.json'

def get_document():
    """Load or create the document."""
    if DOCUMENT_PATH.exists():
        return Document.load(DOCUMENT_PATH)
    else:
        doc = Document(title="CEO Weekly Document - Opportunity at Work")
        doc.save(DOCUMENT_PATH)
        return doc

def get_rules():
    """Load formatting rules."""
    if RULES_PATH.exists():
        return RulesConfig(RULES_PATH)
    return RulesConfig()

def get_link_manager(doc):
    """Get a link manager for the document."""
    return LinkManager(doc)

# ============== Routes ==============

@app.route('/')
def index():
    """Main dashboard showing the document."""
    doc = get_document()
    stats = doc.get_stats()

    # Sort sections by order
    sorted_sections = sorted(
        doc.sections.items(),
        key=lambda x: x[1].sort_order
    )

    return render_template('index.html',
                         document=doc,
                         sections=sorted_sections,
                         stats=stats)

@app.route('/add', methods=['GET', 'POST'])
def add_link():
    """Add a new link to the document."""
    if request.method == 'POST':
        doc = get_document()
        manager = get_link_manager(doc)

        url = request.form.get('url', '').strip()
        title = request.form.get('title', '').strip()
        summary = request.form.get('summary', '').strip()
        section = request.form.get('section', 'this_week')
        category = request.form.get('category', 'reading')
        priority = int(request.form.get('priority', 0))
        tags_str = request.form.get('tags', '').strip()
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        source = request.form.get('source', '')

        if not url or not title:
            flash('URL and Title are required', 'error')
            return redirect(url_for('add_link'))

        entry = manager.add_link(
            url=url,
            title=title,
            summary=summary,
            section=section,
            category=category,
            tags=tags,
            priority=priority,
            source=source
        )

        if entry:
            doc.save(DOCUMENT_PATH)
            flash(f'Added: {title}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to add link (may be duplicate)', 'error')
            return redirect(url_for('add_link'))

    # GET request - show form
    doc = get_document()
    sections = list(doc.sections.keys())
    return render_template('add_link.html', sections=sections)

@app.route('/edit/<path:url_encoded>', methods=['GET', 'POST'])
def edit_link(url_encoded):
    """Edit an existing link."""
    from urllib.parse import unquote
    url = unquote(url_encoded)

    doc = get_document()
    entry = doc.find_entry(url)

    if not entry:
        flash('Entry not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        manager = get_link_manager(doc)

        new_title = request.form.get('title', '').strip()
        new_summary = request.form.get('summary', '').strip()
        new_status = request.form.get('status', 'new')
        new_priority = int(request.form.get('priority', 0))
        tags_str = request.form.get('tags', '').strip()
        new_tags = [t.strip() for t in tags_str.split(',') if t.strip()]

        manager.update_link(
            url=url,
            title=new_title if new_title else None,
            summary=new_summary if new_summary else None,
            status=new_status,
            tags=new_tags,
            priority=new_priority
        )

        doc.save(DOCUMENT_PATH)
        flash('Entry updated', 'success')
        return redirect(url_for('index'))

    # GET request - show form
    sections = list(doc.sections.keys())
    return render_template('edit_link.html', entry=entry, sections=sections)

@app.route('/delete/<path:url_encoded>', methods=['POST'])
def delete_link(url_encoded):
    """Delete a link."""
    from urllib.parse import unquote
    url = unquote(url_encoded)

    doc = get_document()
    if doc.remove_entry(url):
        doc.save(DOCUMENT_PATH)
        flash('Entry removed', 'success')
    else:
        flash('Entry not found', 'error')

    return redirect(url_for('index'))

@app.route('/move/<path:url_encoded>', methods=['POST'])
def move_link(url_encoded):
    """Move a link to a different section."""
    from urllib.parse import unquote
    url = unquote(url_encoded)
    new_section = request.form.get('section', 'this_week')

    doc = get_document()
    if doc.move_entry(url, new_section):
        doc.save(DOCUMENT_PATH)
        flash(f'Moved to {new_section}', 'success')
    else:
        flash('Failed to move entry', 'error')

    return redirect(url_for('index'))

@app.route('/format', methods=['POST'])
def format_document():
    """Apply formatting rules to the document."""
    doc = get_document()
    rules = get_rules()
    engine = FormatEngine(rules)

    changes = engine.format_document(doc)
    doc.save(DOCUMENT_PATH)

    if changes:
        flash(f'Applied {len(changes)} formatting changes', 'success')
    else:
        flash('No formatting changes needed', 'info')

    return redirect(url_for('index'))

@app.route('/export/<format_type>')
def export_document(format_type):
    """Export document in various formats."""
    doc = get_document()

    export_dir = DATA_DIR / 'exports'
    export_dir.mkdir(exist_ok=True)

    if format_type == 'markdown':
        output_path = export_dir / 'weekly_document.md'
        doc.export_markdown(output_path)
        return send_file(output_path, as_attachment=True, download_name='weekly_document.md')

    elif format_type == 'html':
        from document_link_manager.format_engine import StyleFormatter
        output_path = export_dir / 'weekly_document.html'
        html_content = StyleFormatter.document_to_html(doc)
        with open(output_path, 'w') as f:
            f.write(html_content)
        return send_file(output_path, as_attachment=True, download_name='weekly_document.html')

    elif format_type == 'json':
        output_path = export_dir / 'weekly_document_export.json'
        with open(output_path, 'w') as f:
            json.dump(doc.to_dict(), f, indent=2)
        return send_file(output_path, as_attachment=True, download_name='weekly_document.json')

    flash('Unknown export format', 'error')
    return redirect(url_for('index'))

@app.route('/quick-add', methods=['POST'])
def quick_add():
    """Quick add a link with just URL - auto-detect title."""
    url = request.form.get('url', '').strip()

    if not url:
        flash('URL is required', 'error')
        return redirect(url_for('index'))

    doc = get_document()
    manager = get_link_manager(doc)

    # Parse the URL to generate a basic title
    link_info = manager.parse_url(url)
    title = manager._generate_title_from_url(url, link_info)

    entry = manager.add_link(
        url=url,
        title=title,
        section=manager.suggest_section(link_info),
        category=manager.suggest_category(link_info),
        source='quick_add'
    )

    if entry:
        # Auto-apply formatting
        rules = get_rules()
        engine = FormatEngine(rules)
        engine.format_document(doc)
        doc.save(DOCUMENT_PATH)
        flash(f'Added: {title}', 'success')
    else:
        flash('Failed to add link (may be duplicate)', 'error')

    return redirect(url_for('index'))

@app.route('/update-status/<path:url_encoded>', methods=['POST'])
def update_status(url_encoded):
    """Quick update entry status."""
    from urllib.parse import unquote
    url = unquote(url_encoded)
    new_status = request.form.get('status', 'new')

    doc = get_document()
    manager = get_link_manager(doc)

    if manager.update_link(url=url, status=new_status):
        # Re-apply formatting for color updates
        rules = get_rules()
        engine = FormatEngine(rules)
        engine.format_document(doc)
        doc.save(DOCUMENT_PATH)
        flash(f'Status updated to {new_status}', 'success')
    else:
        flash('Failed to update status', 'error')

    return redirect(url_for('index'))

@app.route('/api/entries')
def api_entries():
    """API endpoint to get all entries as JSON."""
    doc = get_document()
    entries = []

    for section_key, section in doc.sections.items():
        for entry in section.entries:
            entry_dict = entry.to_dict()
            entry_dict['section'] = section_key
            entries.append(entry_dict)

    return jsonify(entries)

@app.route('/api/add', methods=['POST'])
def api_add():
    """API endpoint to add a link."""
    data = request.get_json()

    if not data or not data.get('url'):
        return jsonify({'error': 'URL is required'}), 400

    doc = get_document()
    manager = get_link_manager(doc)

    entry = manager.add_link(
        url=data.get('url'),
        title=data.get('title', ''),
        summary=data.get('summary', ''),
        section=data.get('section', 'this_week'),
        category=data.get('category'),
        tags=data.get('tags', []),
        priority=data.get('priority', 0),
        source=data.get('source', 'api')
    )

    if entry:
        rules = get_rules()
        engine = FormatEngine(rules)
        engine.format_document(doc)
        doc.save(DOCUMENT_PATH)
        return jsonify({'success': True, 'entry': entry.to_dict()})

    return jsonify({'error': 'Failed to add (may be duplicate)'}), 400

@app.route('/rules')
def view_rules():
    """View and edit formatting rules."""
    rules = get_rules()
    return render_template('rules.html', rules=rules)


# ============== Template Filters ==============

@app.template_filter('datetime')
def format_datetime(value):
    """Format ISO datetime string."""
    if not value:
        return ''
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime('%b %d, %Y')
    except:
        return value[:10] if len(value) >= 10 else value

@app.template_filter('urlencode')
def urlencode_filter(value):
    """URL encode a string."""
    from urllib.parse import quote
    return quote(value, safe='')


# ============== Main ==============

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Document Link Manager - Web Interface")
    print("="*50)
    print(f"\n  Open in browser: http://localhost:5000")
    print(f"\n  Document: {DOCUMENT_PATH}")
    print(f"  Rules: {RULES_PATH}")
    print("\n" + "="*50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
