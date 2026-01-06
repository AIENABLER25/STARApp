"""
Sentiment Analysis Module
Analyzes sentiment of Reddit posts and comments about layoffs and unemployment
"""
import re
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import Counter
import logging

# Sentiment analysis libraries
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SENTIMENT_THRESHOLDS, DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)


@dataclass
class SentimentResult:
    """Data class for sentiment analysis results"""
    text_id: str
    text_type: str  # 'post' or 'comment'
    original_text: str
    cleaned_text: str
    vader_compound: float
    vader_positive: float
    vader_negative: float
    vader_neutral: float
    textblob_polarity: float
    textblob_subjectivity: float
    combined_score: float
    sentiment_label: str
    confidence: float
    key_phrases: List[str]
    emotion_indicators: Dict[str, int]


class SentimentAnalyzer:
    """
    Multi-method sentiment analyzer for layoff-related discussions
    """

    def __init__(self):
        """Initialize sentiment analyzers"""
        self.vader = SentimentIntensityAnalyzer()
        self._add_layoff_lexicon()

        # Emotion keywords for deeper analysis
        self.emotion_keywords = {
            "fear": ["scared", "afraid", "terrified", "anxious", "worried", "nervous", "panic", "dread"],
            "anger": ["angry", "furious", "outraged", "pissed", "frustrated", "mad", "livid", "bitter"],
            "sadness": ["sad", "depressed", "devastated", "heartbroken", "miserable", "hopeless", "grief", "despair"],
            "hope": ["hopeful", "optimistic", "confident", "positive", "encouraged", "motivated", "excited"],
            "relief": ["relieved", "grateful", "thankful", "blessed", "lucky", "fortunate"],
            "frustration": ["frustrated", "annoyed", "irritated", "stuck", "trapped", "helpless"],
            "stress": ["stressed", "overwhelmed", "burned out", "exhausted", "drained", "tired"],
            "uncertainty": ["uncertain", "confused", "lost", "unsure", "unclear", "ambiguous"],
        }

    def _add_layoff_lexicon(self):
        """Add layoff-specific words to VADER lexicon"""
        new_words = {
            "layoff": -2.5,
            "laid off": -2.5,
            "fired": -3.0,
            "terminated": -2.5,
            "unemployed": -2.0,
            "underemployed": -1.5,
            "downsizing": -2.0,
            "restructuring": -1.5,
            "severance": -1.0,
            "furlough": -2.0,
            "pink slip": -2.5,
            "job loss": -2.5,
            "workforce reduction": -2.0,
            "hiring freeze": -1.5,
            "job cuts": -2.0,
            "mass layoff": -3.0,
            "ghost job": -1.5,
            "rejected": -1.5,
            "ghosted": -1.5,
            "burnout": -2.0,
            "toxic": -2.0,
            "overworked": -1.5,
            "underpaid": -1.5,
            "new job": 2.0,
            "offer": 1.5,
            "hired": 2.5,
            "promoted": 2.0,
            "raise": 1.5,
            "interview": 0.5,
            "opportunity": 1.0,
            "upskill": 1.0,
            "networking": 0.5,
        }
        self.vader.lexicon.update(new_words)

    def clean_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        if not text:
            return ""

        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Remove Reddit-specific formatting
        text = re.sub(r'/r/\w+', '', text)  # Remove subreddit references
        text = re.sub(r'/u/\w+', '', text)  # Remove user references
        text = re.sub(r'\[deleted\]|\[removed\]', '', text)

        # Remove special characters but keep punctuation for sentiment
        text = re.sub(r'[^\w\s.,!?\'"-]', ' ', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text.strip()

    def analyze_text(self, text: str, text_id: str, text_type: str = "post") -> SentimentResult:
        """
        Analyze sentiment of a single text

        Args:
            text: Text to analyze
            text_id: Unique identifier for the text
            text_type: Type of text ('post' or 'comment')

        Returns:
            SentimentResult object
        """
        cleaned_text = self.clean_text(text)

        if not cleaned_text:
            return self._empty_result(text_id, text_type, text)

        # VADER sentiment analysis
        vader_scores = self.vader.polarity_scores(cleaned_text)

        # TextBlob sentiment analysis
        blob = TextBlob(cleaned_text)
        textblob_polarity = blob.sentiment.polarity
        textblob_subjectivity = blob.sentiment.subjectivity

        # Combined score (weighted average)
        combined_score = (vader_scores['compound'] * 0.6) + (textblob_polarity * 0.4)

        # Determine sentiment label
        sentiment_label = self._get_sentiment_label(combined_score)

        # Calculate confidence based on agreement between analyzers
        confidence = self._calculate_confidence(vader_scores['compound'], textblob_polarity)

        # Extract key phrases
        key_phrases = self._extract_key_phrases(cleaned_text)

        # Detect emotions
        emotion_indicators = self._detect_emotions(cleaned_text)

        return SentimentResult(
            text_id=text_id,
            text_type=text_type,
            original_text=text[:500] + "..." if len(text) > 500 else text,
            cleaned_text=cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text,
            vader_compound=vader_scores['compound'],
            vader_positive=vader_scores['pos'],
            vader_negative=vader_scores['neg'],
            vader_neutral=vader_scores['neu'],
            textblob_polarity=textblob_polarity,
            textblob_subjectivity=textblob_subjectivity,
            combined_score=combined_score,
            sentiment_label=sentiment_label,
            confidence=confidence,
            key_phrases=key_phrases,
            emotion_indicators=emotion_indicators,
        )

    def _empty_result(self, text_id: str, text_type: str, original_text: str) -> SentimentResult:
        """Return empty result for invalid text"""
        return SentimentResult(
            text_id=text_id,
            text_type=text_type,
            original_text=original_text[:100] if original_text else "",
            cleaned_text="",
            vader_compound=0.0,
            vader_positive=0.0,
            vader_negative=0.0,
            vader_neutral=1.0,
            textblob_polarity=0.0,
            textblob_subjectivity=0.0,
            combined_score=0.0,
            sentiment_label="neutral",
            confidence=0.0,
            key_phrases=[],
            emotion_indicators={},
        )

    def _get_sentiment_label(self, score: float) -> str:
        """Convert numeric sentiment score to label"""
        if score <= SENTIMENT_THRESHOLDS["very_negative"]:
            return "very_negative"
        elif score <= SENTIMENT_THRESHOLDS["negative"]:
            return "negative"
        elif score <= SENTIMENT_THRESHOLDS["neutral"]:
            return "neutral"
        elif score <= SENTIMENT_THRESHOLDS["positive"]:
            return "positive"
        else:
            return "very_positive"

    def _calculate_confidence(self, vader_score: float, textblob_score: float) -> float:
        """Calculate confidence based on analyzer agreement"""
        # Both scores should be in similar direction
        same_direction = (vader_score * textblob_score) >= 0

        if same_direction:
            # Higher confidence when both agree
            diff = abs(vader_score - textblob_score)
            confidence = max(0.5, 1.0 - diff)
        else:
            # Lower confidence when they disagree
            confidence = 0.3 + (0.2 * (1 - abs(vader_score - textblob_score)))

        return round(confidence, 2)

    def _extract_key_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """Extract key phrases from text using noun phrase extraction"""
        try:
            blob = TextBlob(text)
            noun_phrases = blob.noun_phrases

            # Filter and limit phrases
            key_phrases = [
                phrase for phrase in noun_phrases
                if len(phrase.split()) <= 4 and len(phrase) > 3
            ][:max_phrases]

            return key_phrases
        except Exception:
            return []

    def _detect_emotions(self, text: str) -> Dict[str, int]:
        """Detect emotion indicators in text"""
        text_lower = text.lower()
        emotions = {}

        for emotion, keywords in self.emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                emotions[emotion] = count

        return emotions

    def analyze_posts(self, posts: List[Dict]) -> List[SentimentResult]:
        """Analyze sentiment of multiple posts"""
        results = []
        for post in posts:
            # Combine title and body for analysis
            full_text = f"{post.get('title', '')} {post.get('selftext', '')}"
            result = self.analyze_text(full_text, post.get('id', ''), 'post')
            results.append(result)
        return results

    def analyze_comments(self, comments: List[Dict]) -> List[SentimentResult]:
        """Analyze sentiment of multiple comments"""
        results = []
        for comment in comments:
            result = self.analyze_text(
                comment.get('body', ''),
                comment.get('id', ''),
                'comment'
            )
            results.append(result)
        return results

    def get_aggregate_sentiment(self, results: List[SentimentResult]) -> Dict:
        """Calculate aggregate sentiment statistics"""
        if not results:
            return {"error": "No results to aggregate"}

        scores = [r.combined_score for r in results]
        labels = [r.sentiment_label for r in results]

        # Aggregate emotions
        all_emotions = Counter()
        for result in results:
            all_emotions.update(result.emotion_indicators)

        # Calculate statistics
        return {
            "total_analyzed": len(results),
            "average_score": sum(scores) / len(scores),
            "median_score": sorted(scores)[len(scores) // 2],
            "min_score": min(scores),
            "max_score": max(scores),
            "score_std": self._std_dev(scores),
            "sentiment_distribution": dict(Counter(labels)),
            "emotion_summary": dict(all_emotions.most_common(10)),
            "most_negative": min(results, key=lambda x: x.combined_score),
            "most_positive": max(results, key=lambda x: x.combined_score),
        }

    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def analyze_reddit_data(self, data: Dict) -> Dict:
        """
        Analyze complete Reddit data including posts and comments

        Args:
            data: Dictionary containing posts and comments

        Returns:
            Dictionary with analysis results
        """
        posts = data.get('posts', [])
        comments = data.get('comments', [])

        logger.info(f"Analyzing {len(posts)} posts and {len(comments)} comments...")

        # Analyze posts and comments
        post_results = self.analyze_posts(posts)
        comment_results = self.analyze_comments(comments)

        # Combine results
        all_results = post_results + comment_results

        # Calculate aggregates
        post_aggregate = self.get_aggregate_sentiment(post_results)
        comment_aggregate = self.get_aggregate_sentiment(comment_results)
        overall_aggregate = self.get_aggregate_sentiment(all_results)

        # Analyze by subreddit
        subreddit_sentiment = self._analyze_by_subreddit(posts, post_results)

        return {
            "post_results": [asdict(r) for r in post_results],
            "comment_results": [asdict(r) for r in comment_results],
            "post_aggregate": {
                k: (asdict(v) if isinstance(v, SentimentResult) else v)
                for k, v in post_aggregate.items()
            },
            "comment_aggregate": {
                k: (asdict(v) if isinstance(v, SentimentResult) else v)
                for k, v in comment_aggregate.items()
            },
            "overall_aggregate": {
                k: (asdict(v) if isinstance(v, SentimentResult) else v)
                for k, v in overall_aggregate.items()
            },
            "subreddit_sentiment": subreddit_sentiment,
        }

    def _analyze_by_subreddit(
        self,
        posts: List[Dict],
        results: List[SentimentResult]
    ) -> Dict[str, Dict]:
        """Analyze sentiment grouped by subreddit"""
        subreddit_results = {}

        for post, result in zip(posts, results):
            subreddit = post.get('subreddit', 'unknown')
            if subreddit not in subreddit_results:
                subreddit_results[subreddit] = []
            subreddit_results[subreddit].append(result)

        # Calculate aggregates per subreddit
        subreddit_sentiment = {}
        for subreddit, sub_results in subreddit_results.items():
            scores = [r.combined_score for r in sub_results]
            labels = [r.sentiment_label for r in sub_results]

            subreddit_sentiment[subreddit] = {
                "post_count": len(sub_results),
                "average_score": sum(scores) / len(scores) if scores else 0,
                "sentiment_distribution": dict(Counter(labels)),
                "dominant_sentiment": max(set(labels), key=labels.count) if labels else "neutral",
            }

        return subreddit_sentiment

    def save_results(self, results: Dict, filename: str = "sentiment_results.json"):
        """Save analysis results to JSON file"""
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to {filepath}")
        return filepath

    def load_results(self, filename: str = "sentiment_results.json") -> Optional[Dict]:
        """Load previously saved results"""
        filepath = os.path.join(DATA_DIR, filename)

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


def main():
    """Main function to run sentiment analysis"""
    from reddit_scraper import RedditScraper

    # Load or scrape data
    scraper = RedditScraper(use_sample_data=True)
    data = scraper.load_data()

    if not data:
        print("No data found. Running scraper first...")
        data = scraper.scrape_all()
        scraper.save_data(data)

    # Run sentiment analysis
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze_reddit_data(data)

    # Save results
    analyzer.save_results(results)

    # Print summary
    print("\n" + "=" * 60)
    print("SENTIMENT ANALYSIS SUMMARY")
    print("=" * 60)

    overall = results['overall_aggregate']
    print(f"\nTotal texts analyzed: {overall['total_analyzed']}")
    print(f"Average sentiment score: {overall['average_score']:.3f}")
    print(f"\nSentiment distribution:")
    for label, count in overall['sentiment_distribution'].items():
        print(f"  {label}: {count}")

    print(f"\nTop emotions detected:")
    for emotion, count in list(overall['emotion_summary'].items())[:5]:
        print(f"  {emotion}: {count}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
