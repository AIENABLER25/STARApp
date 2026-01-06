"""
Configuration settings for the Reddit Layoff Sentiment Analysis App
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Reddit API Configuration
REDDIT_CONFIG = {
    "client_id": os.getenv("REDDIT_CLIENT_ID", ""),
    "client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
    "user_agent": os.getenv("REDDIT_USER_AGENT", "LayoffSentimentAnalyzer/1.0"),
}

# Subreddits to scrape for layoff/unemployment discussions
TARGET_SUBREDDITS = [
    "layoffs",
    "jobs",
    "careerguidance",
    "cscareerquestions",
    "recruitinghell",
    "antiwork",
    "workreform",
    "unemployed",
    "personalfinance",
    "technology",
    "news",
    "economics",
    "finance",
    "accounting",
    "nursing",
    "teachers",
    "engineering",
    "sales",
    "marketing",
    "humanresources",
]

# Search keywords for layoff-related content
SEARCH_KEYWORDS = [
    "layoff",
    "laid off",
    "fired",
    "unemployment",
    "underemployed",
    "job loss",
    "downsizing",
    "restructuring",
    "workforce reduction",
    "pink slip",
    "terminated",
    "let go",
    "job cuts",
    "mass layoffs",
    "hiring freeze",
    "furlough",
    "severance",
]

# Sector keywords for classification
SECTOR_KEYWORDS = {
    "Technology": [
        "tech", "software", "developer", "engineer", "IT", "programmer",
        "data scientist", "machine learning", "AI", "cloud", "SaaS",
        "startup", "FAANG", "Google", "Meta", "Amazon", "Microsoft",
        "Apple", "Netflix", "coding", "DevOps", "cybersecurity", "fintech"
    ],
    "Finance & Banking": [
        "bank", "finance", "trading", "investment", "hedge fund", "private equity",
        "venture capital", "analyst", "accountant", "CPA", "audit", "tax",
        "wealth management", "insurance", "mortgage", "loan", "credit"
    ],
    "Healthcare": [
        "hospital", "nurse", "doctor", "medical", "healthcare", "pharma",
        "pharmaceutical", "biotech", "clinical", "patient", "health",
        "therapist", "physician", "dental", "laboratory", "research"
    ],
    "Retail & E-commerce": [
        "retail", "store", "shop", "ecommerce", "Amazon", "Walmart", "Target",
        "sales associate", "customer service", "warehouse", "logistics",
        "supply chain", "merchandising", "buyer"
    ],
    "Manufacturing": [
        "manufacturing", "factory", "production", "assembly", "industrial",
        "automotive", "aerospace", "machinery", "plant", "operations",
        "quality control", "supply chain"
    ],
    "Media & Entertainment": [
        "media", "entertainment", "journalism", "news", "TV", "film", "movie",
        "streaming", "Disney", "Warner", "NBC", "content", "creative",
        "advertising", "marketing", "PR", "social media", "influencer"
    ],
    "Education": [
        "teacher", "professor", "school", "university", "college", "education",
        "instructor", "tutor", "academic", "faculty", "principal", "dean"
    ],
    "Real Estate & Construction": [
        "real estate", "construction", "builder", "contractor", "architect",
        "property", "housing", "mortgage", "commercial real estate",
        "residential", "development"
    ],
    "Hospitality & Travel": [
        "hotel", "restaurant", "travel", "tourism", "airline", "hospitality",
        "chef", "server", "bartender", "cruise", "vacation", "booking"
    ],
    "Consulting & Professional Services": [
        "consulting", "consultant", "McKinsey", "Bain", "BCG", "Deloitte",
        "PwC", "EY", "KPMG", "Accenture", "strategy", "management consulting"
    ],
    "Government & Public Sector": [
        "government", "federal", "state", "public sector", "civil service",
        "military", "contractor", "defense", "agency"
    ],
    "Energy & Utilities": [
        "energy", "oil", "gas", "renewable", "solar", "wind", "utility",
        "power", "electric", "petroleum", "mining"
    ],
    "Legal": [
        "lawyer", "attorney", "law firm", "legal", "paralegal", "litigation",
        "corporate law", "BigLaw"
    ],
    "Other/Unknown": []
}

# Sentiment thresholds
SENTIMENT_THRESHOLDS = {
    "very_negative": -0.6,
    "negative": -0.2,
    "neutral": 0.2,
    "positive": 0.6,
    "very_positive": 1.0,
}

# Output settings
OUTPUT_DIR = "output"
DATA_DIR = "data"

# Scraping limits
MAX_POSTS_PER_SUBREDDIT = 100
MAX_COMMENTS_PER_POST = 50
RATE_LIMIT_DELAY = 2  # seconds between requests
