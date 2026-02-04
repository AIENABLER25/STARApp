"""
Rules Configuration - Defines and manages formatting rules.

Supports loading rules from YAML/JSON and applying them to documents.
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class RuleType(Enum):
    """Types of formatting rules."""
    COLOR = "color"
    STYLE = "style"
    SORT = "sort"
    SECTION = "section"
    TAG = "tag"
    VALIDATION = "validation"


class MatchType(Enum):
    """How to match content for rule application."""
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX = "regex"
    EQUALS = "equals"
    DOMAIN = "domain"
    CATEGORY = "category"
    STATUS = "status"
    TAG = "tag"
    PRIORITY = "priority"


@dataclass
class RuleCondition:
    """A condition for when a rule should apply."""
    field: str  # title, url, summary, category, status, tags, priority, domain
    match_type: str  # contains, starts_with, regex, equals, domain
    value: Any  # The value to match against

    def matches(self, entry_data: dict) -> bool:
        """Check if this condition matches the entry data."""
        field_value = entry_data.get(self.field, "")

        # Handle list fields (like tags)
        if isinstance(field_value, list):
            field_value = " ".join(str(v) for v in field_value)
        else:
            field_value = str(field_value)

        match_type = MatchType(self.match_type)
        value = str(self.value)

        if match_type == MatchType.CONTAINS:
            return value.lower() in field_value.lower()

        elif match_type == MatchType.STARTS_WITH:
            return field_value.lower().startswith(value.lower())

        elif match_type == MatchType.ENDS_WITH:
            return field_value.lower().endswith(value.lower())

        elif match_type == MatchType.EQUALS:
            return field_value.lower() == value.lower()

        elif match_type == MatchType.REGEX:
            try:
                return bool(re.search(value, field_value, re.IGNORECASE))
            except re.error:
                return False

        elif match_type == MatchType.DOMAIN:
            # Extract domain from URL
            from urllib.parse import urlparse
            try:
                domain = urlparse(field_value).netloc.lower()
                return value.lower() in domain
            except Exception:
                return False

        return False


@dataclass
class FormattingRule:
    """A single formatting rule."""
    name: str
    description: str = ""
    conditions: list = field(default_factory=list)  # List of RuleCondition dicts
    action: str = ""  # What to do when matched
    action_value: Any = None  # Value for the action
    priority: int = 0  # Higher priority rules are applied first
    enabled: bool = True

    def matches(self, entry_data: dict) -> bool:
        """Check if all conditions match (AND logic)."""
        if not self.conditions:
            return False

        for cond_dict in self.conditions:
            condition = RuleCondition(**cond_dict)
            if not condition.matches(entry_data):
                return False

        return True


@dataclass
class SectionRule:
    """Rule for organizing entries into sections."""
    section_name: str
    conditions: list = field(default_factory=list)
    priority: int = 0


class RulesConfig:
    """
    Configuration manager for document formatting rules.

    Supports:
    - Color rules (based on status, category, domain, etc.)
    - Section assignment rules
    - Sorting rules
    - Validation rules
    - Auto-tagging rules
    """

    DEFAULT_COLORS = {
        "priority": {
            1: "#FFE066",  # Yellow - Low priority
            2: "#FFA500",  # Orange - Medium priority
            3: "#FF6B6B",  # Red - High priority
            4: "#FF0000",  # Bright red - Urgent
            5: "#8B0000",  # Dark red - Critical
        },
        "status": {
            "new": "#4ECDC4",      # Teal
            "in_progress": "#45B7D1",  # Blue
            "completed": "#96CEB4",    # Green
            "archived": "#95A5A6",     # Gray
        },
        "category": {
            "reading": "#45B7D1",     # Blue
            "action_item": "#FF6B6B", # Red
            "reference": "#DDA0DD",   # Plum
            "meeting": "#F7DC6F",     # Yellow
            "research": "#BB8FCE",    # Purple
            "follow_up": "#FFA500",   # Orange
            "idea": "#96CEB4",        # Green
        }
    }

    DEFAULT_SECTION_ORDER = [
        "priority",
        "this_week",
        "action_items",
        "reading_list",
        "follow_up",
        "references",
        "ideas",
        "archive"
    ]

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize rules configuration.

        Args:
            config_path: Path to rules configuration file
        """
        self.config_path = config_path
        self.formatting_rules: list[FormattingRule] = []
        self.section_rules: list[SectionRule] = []
        self.color_overrides: dict = {}
        self.section_order: list[str] = self.DEFAULT_SECTION_ORDER.copy()
        self.custom_settings: dict = {}

        if config_path and Path(config_path).exists():
            self.load(config_path)
        else:
            self._init_default_rules()

    def _init_default_rules(self):
        """Initialize default formatting rules."""
        # Priority coloring rules
        self.formatting_rules.extend([
            FormattingRule(
                name="high_priority_color",
                description="Color high priority items red",
                conditions=[{"field": "priority", "match_type": "equals", "value": "3"}],
                action="color",
                action_value="#FF6B6B",
                priority=100
            ),
            FormattingRule(
                name="urgent_priority_color",
                description="Color urgent items bright red",
                conditions=[{"field": "priority", "match_type": "equals", "value": "4"}],
                action="color",
                action_value="#FF0000",
                priority=100
            ),
            FormattingRule(
                name="completed_color",
                description="Color completed items green",
                conditions=[{"field": "status", "match_type": "equals", "value": "completed"}],
                action="color",
                action_value="#96CEB4",
                priority=50
            ),
            FormattingRule(
                name="archived_color",
                description="Gray out archived items",
                conditions=[{"field": "status", "match_type": "equals", "value": "archived"}],
                action="color",
                action_value="#95A5A6",
                priority=50
            ),
        ])

        # Platform-specific rules
        self.formatting_rules.extend([
            FormattingRule(
                name="linkedin_tag",
                description="Auto-tag LinkedIn content",
                conditions=[{"field": "url", "match_type": "domain", "value": "linkedin.com"}],
                action="add_tag",
                action_value="linkedin",
                priority=10
            ),
            FormattingRule(
                name="twitter_tag",
                description="Auto-tag Twitter content",
                conditions=[{"field": "url", "match_type": "domain", "value": "twitter.com"}],
                action="add_tag",
                action_value="twitter",
                priority=10
            ),
            FormattingRule(
                name="youtube_tag",
                description="Auto-tag YouTube content",
                conditions=[{"field": "url", "match_type": "domain", "value": "youtube.com"}],
                action="add_tag",
                action_value="video",
                priority=10
            ),
        ])

        # Section assignment rules
        self.section_rules.extend([
            SectionRule(
                section_name="priority",
                conditions=[{"field": "priority", "match_type": "equals", "value": "3"}],
                priority=100
            ),
            SectionRule(
                section_name="action_items",
                conditions=[{"field": "category", "match_type": "equals", "value": "action_item"}],
                priority=50
            ),
            SectionRule(
                section_name="reading_list",
                conditions=[{"field": "category", "match_type": "equals", "value": "reading"}],
                priority=40
            ),
        ])

    def load(self, path: Path):
        """Load rules from a JSON configuration file."""
        path = Path(path)

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Load formatting rules
        self.formatting_rules = [
            FormattingRule(**rule)
            for rule in data.get("formatting_rules", [])
        ]

        # Load section rules
        self.section_rules = [
            SectionRule(**rule)
            for rule in data.get("section_rules", [])
        ]

        # Load other settings
        self.color_overrides = data.get("color_overrides", {})
        self.section_order = data.get("section_order", self.DEFAULT_SECTION_ORDER)
        self.custom_settings = data.get("custom_settings", {})

        self.config_path = path

    def save(self, path: Optional[Path] = None):
        """Save rules to a JSON configuration file."""
        save_path = path or self.config_path
        if not save_path:
            raise ValueError("No path specified for saving")

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "formatting_rules": [
                {
                    "name": r.name,
                    "description": r.description,
                    "conditions": r.conditions,
                    "action": r.action,
                    "action_value": r.action_value,
                    "priority": r.priority,
                    "enabled": r.enabled
                }
                for r in self.formatting_rules
            ],
            "section_rules": [
                {
                    "section_name": r.section_name,
                    "conditions": r.conditions,
                    "priority": r.priority
                }
                for r in self.section_rules
            ],
            "color_overrides": self.color_overrides,
            "section_order": self.section_order,
            "custom_settings": self.custom_settings
        }

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        self.config_path = save_path

    def add_rule(self, rule: FormattingRule):
        """Add a new formatting rule."""
        self.formatting_rules.append(rule)
        # Sort by priority (highest first)
        self.formatting_rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        for i, rule in enumerate(self.formatting_rules):
            if rule.name == rule_name:
                self.formatting_rules.pop(i)
                return True
        return False

    def get_applicable_rules(self, entry_data: dict) -> list[FormattingRule]:
        """Get all rules that apply to an entry."""
        applicable = []
        for rule in self.formatting_rules:
            if rule.enabled and rule.matches(entry_data):
                applicable.append(rule)
        return applicable

    def get_color_for_entry(self, entry_data: dict) -> Optional[str]:
        """
        Determine the color for an entry based on rules.

        Args:
            entry_data: Dictionary of entry fields

        Returns:
            Color hex code or None
        """
        # Check formatting rules first (highest priority)
        for rule in self.formatting_rules:
            if rule.enabled and rule.action == "color" and rule.matches(entry_data):
                return rule.action_value

        # Fall back to default colors
        # Check priority first
        priority = entry_data.get("priority", 0)
        if priority > 0 and priority in self.DEFAULT_COLORS["priority"]:
            return self.DEFAULT_COLORS["priority"][priority]

        # Then check status
        status = entry_data.get("status", "")
        if status in self.DEFAULT_COLORS["status"]:
            return self.DEFAULT_COLORS["status"][status]

        # Then check category
        category = entry_data.get("category", "")
        if category in self.DEFAULT_COLORS["category"]:
            return self.DEFAULT_COLORS["category"][category]

        return None

    def get_section_for_entry(self, entry_data: dict) -> Optional[str]:
        """
        Determine the best section for an entry based on rules.

        Args:
            entry_data: Dictionary of entry fields

        Returns:
            Section key or None
        """
        # Sort section rules by priority
        sorted_rules = sorted(self.section_rules, key=lambda r: r.priority, reverse=True)

        for rule in sorted_rules:
            all_match = True
            for cond_dict in rule.conditions:
                condition = RuleCondition(**cond_dict)
                if not condition.matches(entry_data):
                    all_match = False
                    break

            if all_match:
                return rule.section_name

        return None

    def get_auto_tags(self, entry_data: dict) -> list[str]:
        """
        Get tags that should be automatically added based on rules.

        Args:
            entry_data: Dictionary of entry fields

        Returns:
            List of tag strings to add
        """
        tags = []
        for rule in self.formatting_rules:
            if rule.enabled and rule.action == "add_tag" and rule.matches(entry_data):
                tag = rule.action_value
                if isinstance(tag, list):
                    tags.extend(tag)
                else:
                    tags.append(tag)
        return list(set(tags))  # Remove duplicates

    def validate_entry(self, entry_data: dict) -> list[str]:
        """
        Validate an entry against validation rules.

        Args:
            entry_data: Dictionary of entry fields

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        for rule in self.formatting_rules:
            if rule.enabled and rule.action == "validate":
                if rule.matches(entry_data):
                    # Rule matched - check if it's a negative validation
                    if rule.action_value.get("error"):
                        errors.append(rule.action_value["error"])

        # Built-in validations
        if not entry_data.get("url"):
            errors.append("URL is required")

        if not entry_data.get("title"):
            errors.append("Title is required")

        url = entry_data.get("url", "")
        if url and not (url.startswith("http://") or url.startswith("https://")):
            errors.append("URL must start with http:// or https://")

        return errors

    def create_template(self) -> dict:
        """
        Create a template configuration for users to customize.

        Returns:
            Template dictionary
        """
        return {
            "formatting_rules": [
                {
                    "name": "example_color_rule",
                    "description": "Example: Color items containing 'urgent' in title red",
                    "conditions": [
                        {"field": "title", "match_type": "contains", "value": "urgent"}
                    ],
                    "action": "color",
                    "action_value": "#FF0000",
                    "priority": 100,
                    "enabled": True
                },
                {
                    "name": "example_tag_rule",
                    "description": "Example: Auto-tag items from specific domain",
                    "conditions": [
                        {"field": "url", "match_type": "domain", "value": "example.com"}
                    ],
                    "action": "add_tag",
                    "action_value": "example",
                    "priority": 10,
                    "enabled": True
                }
            ],
            "section_rules": [
                {
                    "section_name": "priority",
                    "conditions": [
                        {"field": "priority", "match_type": "equals", "value": "3"}
                    ],
                    "priority": 100
                }
            ],
            "color_overrides": {
                "status": {
                    "new": "#4ECDC4",
                    "in_progress": "#45B7D1",
                    "completed": "#96CEB4",
                    "archived": "#95A5A6"
                }
            },
            "section_order": [
                "priority",
                "this_week",
                "action_items",
                "reading_list",
                "follow_up",
                "references",
                "ideas",
                "archive"
            ],
            "custom_settings": {
                "auto_archive_completed_after_days": 7,
                "default_section": "this_week"
            }
        }
