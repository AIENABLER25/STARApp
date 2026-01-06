"""
Sector Classification Module
Classifies layoff discussions by industry sector and analyzes sector-specific impacts
"""
import re
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
import logging

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SECTOR_KEYWORDS, DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SectorClassification:
    """Data class for sector classification results"""
    text_id: str
    primary_sector: str
    sector_scores: Dict[str, float]
    confidence: float
    matched_keywords: List[str]
    company_mentions: List[str]


@dataclass
class SectorAnalysis:
    """Data class for sector-level analysis"""
    sector: str
    post_count: int
    total_engagement: int
    average_sentiment: float
    sentiment_distribution: Dict[str, int]
    top_keywords: List[Tuple[str, int]]
    top_emotions: List[Tuple[str, int]]
    sample_posts: List[Dict]


class SectorClassifier:
    """
    Classifies layoff discussions by industry sector
    """

    def __init__(self):
        """Initialize the sector classifier"""
        self.sector_keywords = SECTOR_KEYWORDS
        self._compile_patterns()

        # Company to sector mapping for major companies
        self.company_sector_map = {
            # Tech
            "google": "Technology",
            "alphabet": "Technology",
            "meta": "Technology",
            "facebook": "Technology",
            "amazon": "Technology",
            "microsoft": "Technology",
            "apple": "Technology",
            "netflix": "Technology",
            "twitter": "Technology",
            "x corp": "Technology",
            "salesforce": "Technology",
            "oracle": "Technology",
            "ibm": "Technology",
            "intel": "Technology",
            "nvidia": "Technology",
            "adobe": "Technology",
            "cisco": "Technology",
            "uber": "Technology",
            "lyft": "Technology",
            "airbnb": "Technology",
            "spotify": "Technology",
            "stripe": "Technology",
            "shopify": "Technology",
            "zoom": "Technology",
            "slack": "Technology",
            "dropbox": "Technology",
            "twilio": "Technology",
            "unity": "Technology",
            "epic": "Technology",

            # Finance
            "goldman": "Finance & Banking",
            "goldman sachs": "Finance & Banking",
            "morgan stanley": "Finance & Banking",
            "jpmorgan": "Finance & Banking",
            "jp morgan": "Finance & Banking",
            "chase": "Finance & Banking",
            "bank of america": "Finance & Banking",
            "citibank": "Finance & Banking",
            "citi": "Finance & Banking",
            "wells fargo": "Finance & Banking",
            "barclays": "Finance & Banking",
            "hsbc": "Finance & Banking",
            "blackrock": "Finance & Banking",
            "fidelity": "Finance & Banking",
            "vanguard": "Finance & Banking",

            # Consulting
            "mckinsey": "Consulting & Professional Services",
            "bain": "Consulting & Professional Services",
            "bcg": "Consulting & Professional Services",
            "deloitte": "Consulting & Professional Services",
            "pwc": "Consulting & Professional Services",
            "ey": "Consulting & Professional Services",
            "ernst young": "Consulting & Professional Services",
            "kpmg": "Consulting & Professional Services",
            "accenture": "Consulting & Professional Services",

            # Retail
            "walmart": "Retail & E-commerce",
            "target": "Retail & E-commerce",
            "costco": "Retail & E-commerce",
            "best buy": "Retail & E-commerce",
            "home depot": "Retail & E-commerce",
            "lowes": "Retail & E-commerce",
            "macys": "Retail & E-commerce",
            "nordstrom": "Retail & E-commerce",
            "kohls": "Retail & E-commerce",

            # Healthcare
            "pfizer": "Healthcare",
            "johnson johnson": "Healthcare",
            "unitedhealth": "Healthcare",
            "cvs": "Healthcare",
            "walgreens": "Healthcare",
            "kaiser": "Healthcare",
            "hca": "Healthcare",

            # Media
            "disney": "Media & Entertainment",
            "warner": "Media & Entertainment",
            "paramount": "Media & Entertainment",
            "nbc": "Media & Entertainment",
            "fox": "Media & Entertainment",
            "cnn": "Media & Entertainment",
            "buzzfeed": "Media & Entertainment",
            "vice": "Media & Entertainment",
        }

    def _compile_patterns(self):
        """Compile regex patterns for efficient matching"""
        self.sector_patterns = {}
        for sector, keywords in self.sector_keywords.items():
            if keywords:
                pattern = '|'.join(re.escape(kw.lower()) for kw in keywords)
                self.sector_patterns[sector] = re.compile(pattern, re.IGNORECASE)

    def classify_text(self, text: str, text_id: str) -> SectorClassification:
        """
        Classify a single text by sector

        Args:
            text: Text to classify
            text_id: Unique identifier for the text

        Returns:
            SectorClassification object
        """
        if not text:
            return self._empty_classification(text_id)

        text_lower = text.lower()
        sector_scores = defaultdict(float)
        matched_keywords = []
        company_mentions = []

        # Check for company mentions first (higher weight)
        for company, sector in self.company_sector_map.items():
            if company in text_lower:
                sector_scores[sector] += 2.0
                company_mentions.append(company.title())

        # Check keyword patterns for each sector
        for sector, pattern in self.sector_patterns.items():
            matches = pattern.findall(text_lower)
            if matches:
                sector_scores[sector] += len(matches)
                matched_keywords.extend(matches)

        # Normalize scores
        total_score = sum(sector_scores.values())
        if total_score > 0:
            sector_scores = {k: v / total_score for k, v in sector_scores.items()}

        # Determine primary sector
        if sector_scores:
            primary_sector = max(sector_scores.items(), key=lambda x: x[1])[0]
            confidence = sector_scores[primary_sector]
        else:
            primary_sector = "Other/Unknown"
            confidence = 0.0

        return SectorClassification(
            text_id=text_id,
            primary_sector=primary_sector,
            sector_scores=dict(sector_scores),
            confidence=round(confidence, 3),
            matched_keywords=list(set(matched_keywords))[:10],
            company_mentions=list(set(company_mentions)),
        )

    def _empty_classification(self, text_id: str) -> SectorClassification:
        """Return empty classification for invalid text"""
        return SectorClassification(
            text_id=text_id,
            primary_sector="Other/Unknown",
            sector_scores={},
            confidence=0.0,
            matched_keywords=[],
            company_mentions=[],
        )

    def classify_posts(self, posts: List[Dict]) -> List[SectorClassification]:
        """Classify multiple posts by sector"""
        results = []
        for post in posts:
            full_text = f"{post.get('title', '')} {post.get('selftext', '')} {post.get('subreddit', '')}"
            result = self.classify_text(full_text, post.get('id', ''))
            results.append(result)
        return results

    def analyze_sectors(
        self,
        posts: List[Dict],
        classifications: List[SectorClassification],
        sentiment_results: List[Dict] = None
    ) -> Dict[str, SectorAnalysis]:
        """
        Analyze layoff impact by sector

        Args:
            posts: List of Reddit posts
            classifications: List of sector classifications
            sentiment_results: Optional list of sentiment analysis results

        Returns:
            Dictionary mapping sectors to SectorAnalysis objects
        """
        # Group posts by sector
        sector_posts = defaultdict(list)
        sentiment_map = {}

        if sentiment_results:
            sentiment_map = {r['text_id']: r for r in sentiment_results}

        for post, classification in zip(posts, classifications):
            sector = classification.primary_sector
            post_data = {
                **post,
                'classification': asdict(classification),
                'sentiment': sentiment_map.get(post.get('id'), {}),
            }
            sector_posts[sector].append(post_data)

        # Analyze each sector
        sector_analyses = {}
        for sector, posts_list in sector_posts.items():
            analysis = self._analyze_sector(sector, posts_list)
            sector_analyses[sector] = analysis

        return sector_analyses

    def _analyze_sector(self, sector: str, posts: List[Dict]) -> SectorAnalysis:
        """Analyze a single sector"""
        # Calculate engagement
        total_engagement = sum(
            post.get('score', 0) + post.get('num_comments', 0)
            for post in posts
        )

        # Calculate sentiment
        sentiments = []
        sentiment_labels = []
        emotions = Counter()

        for post in posts:
            if 'sentiment' in post and post['sentiment']:
                sentiments.append(post['sentiment'].get('combined_score', 0))
                sentiment_labels.append(post['sentiment'].get('sentiment_label', 'neutral'))
                if 'emotion_indicators' in post['sentiment']:
                    emotions.update(post['sentiment']['emotion_indicators'])

        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        # Extract top keywords from classifications
        all_keywords = []
        for post in posts:
            if 'classification' in post:
                all_keywords.extend(post['classification'].get('matched_keywords', []))
        top_keywords = Counter(all_keywords).most_common(10)

        # Get sample posts (most engaged)
        sample_posts = sorted(
            posts,
            key=lambda x: x.get('score', 0) + x.get('num_comments', 0),
            reverse=True
        )[:5]

        return SectorAnalysis(
            sector=sector,
            post_count=len(posts),
            total_engagement=total_engagement,
            average_sentiment=round(avg_sentiment, 3),
            sentiment_distribution=dict(Counter(sentiment_labels)),
            top_keywords=top_keywords,
            top_emotions=emotions.most_common(5),
            sample_posts=[{
                'title': p.get('title', ''),
                'score': p.get('score', 0),
                'subreddit': p.get('subreddit', ''),
            } for p in sample_posts],
        )

    def get_sector_rankings(
        self,
        sector_analyses: Dict[str, SectorAnalysis]
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Rank sectors by various metrics

        Returns:
            Dictionary with different ranking criteria
        """
        rankings = {
            "by_post_count": [],
            "by_engagement": [],
            "by_negative_sentiment": [],
            "most_discussed": [],
        }

        for sector, analysis in sector_analyses.items():
            if sector == "Other/Unknown":
                continue

            rankings["by_post_count"].append((sector, analysis.post_count))
            rankings["by_engagement"].append((sector, analysis.total_engagement))
            rankings["by_negative_sentiment"].append((sector, analysis.average_sentiment))

            # Calculate "discussion intensity" (posts * avg engagement)
            avg_engagement = analysis.total_engagement / max(analysis.post_count, 1)
            rankings["most_discussed"].append((sector, avg_engagement))

        # Sort rankings
        rankings["by_post_count"] = sorted(rankings["by_post_count"], key=lambda x: x[1], reverse=True)
        rankings["by_engagement"] = sorted(rankings["by_engagement"], key=lambda x: x[1], reverse=True)
        rankings["by_negative_sentiment"] = sorted(rankings["by_negative_sentiment"], key=lambda x: x[1])
        rankings["most_discussed"] = sorted(rankings["most_discussed"], key=lambda x: x[1], reverse=True)

        return rankings

    def generate_impact_report(
        self,
        sector_analyses: Dict[str, SectorAnalysis],
        rankings: Dict[str, List[Tuple[str, float]]]
    ) -> Dict:
        """Generate a comprehensive sector impact report"""
        # Identify most impacted sectors
        most_impacted = []
        for sector, analysis in sector_analyses.items():
            if sector == "Other/Unknown":
                continue

            impact_score = (
                analysis.post_count * 0.3 +
                (analysis.total_engagement / 100) * 0.3 +
                (1 - (analysis.average_sentiment + 1) / 2) * 0.4  # Normalize sentiment to 0-1
            )
            most_impacted.append({
                "sector": sector,
                "impact_score": round(impact_score, 2),
                "post_count": analysis.post_count,
                "engagement": analysis.total_engagement,
                "sentiment": analysis.average_sentiment,
                "top_emotions": analysis.top_emotions[:3],
            })

        most_impacted.sort(key=lambda x: x['impact_score'], reverse=True)

        return {
            "summary": {
                "total_sectors_analyzed": len(sector_analyses),
                "total_posts": sum(a.post_count for a in sector_analyses.values()),
                "total_engagement": sum(a.total_engagement for a in sector_analyses.values()),
            },
            "most_impacted_sectors": most_impacted[:10],
            "rankings": rankings,
            "sector_details": {
                sector: asdict(analysis)
                for sector, analysis in sector_analyses.items()
            },
        }

    def save_results(self, results: Dict, filename: str = "sector_analysis.json"):
        """Save sector analysis results to JSON file"""
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Sector analysis saved to {filepath}")
        return filepath


def main():
    """Main function to run sector classification and analysis"""
    from reddit_scraper import RedditScraper
    from sentiment_analyzer import SentimentAnalyzer

    # Load data
    scraper = RedditScraper(use_sample_data=True)
    data = scraper.load_data()

    if not data:
        print("No data found. Running scraper first...")
        data = scraper.scrape_all()
        scraper.save_data(data)

    posts = data.get('posts', [])

    # Run sentiment analysis first
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_results = sentiment_analyzer.analyze_reddit_data(data)

    # Classify and analyze by sector
    classifier = SectorClassifier()
    classifications = classifier.classify_posts(posts)

    sector_analyses = classifier.analyze_sectors(
        posts,
        classifications,
        sentiment_results.get('post_results', [])
    )

    rankings = classifier.get_sector_rankings(sector_analyses)
    report = classifier.generate_impact_report(sector_analyses, rankings)

    # Save results
    classifier.save_results(report)

    # Print summary
    print("\n" + "=" * 60)
    print("SECTOR IMPACT ANALYSIS")
    print("=" * 60)

    print("\nMost Impacted Sectors (by combined impact score):")
    for i, sector in enumerate(report['most_impacted_sectors'][:5], 1):
        print(f"\n{i}. {sector['sector']}")
        print(f"   Impact Score: {sector['impact_score']}")
        print(f"   Posts: {sector['post_count']}, Engagement: {sector['engagement']}")
        print(f"   Avg Sentiment: {sector['sentiment']:.3f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
