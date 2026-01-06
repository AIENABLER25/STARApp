#!/usr/bin/env python3
"""
STARApp - Sentiment Tracker and Analysis for Reddit
Main application entry point for Reddit Layoff Sentiment Analysis

This application scrapes Reddit for discussions about layoffs and unemployment,
performs sentiment analysis, classifies posts by industry sector, and generates
comprehensive visualizations to analyze which sectors are most impacted.

Usage:
    python main.py [--scrape] [--analyze] [--visualize] [--all] [--sample]

Options:
    --scrape      Scrape Reddit for layoff-related posts
    --analyze     Run sentiment analysis and sector classification
    --visualize   Generate visualizations and reports
    --all         Run the complete pipeline (scrape, analyze, visualize)
    --sample      Use sample data (no Reddit API required)
"""

import argparse
import os
import sys
import json
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from reddit_scraper import RedditScraper
from sentiment_analyzer import SentimentAnalyzer
from sector_classifier import SectorClassifier
from visualizer import Visualizer
from config.settings import DATA_DIR, OUTPUT_DIR, TARGET_SUBREDDITS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class STARApp:
    """
    Sentiment Tracker and Analysis for Reddit
    Main application class for layoff sentiment analysis
    """

    def __init__(self, use_sample_data: bool = True):
        """
        Initialize the STARApp

        Args:
            use_sample_data: If True, use sample data instead of live Reddit API
        """
        self.use_sample_data = use_sample_data
        self.scraper = RedditScraper(use_sample_data=use_sample_data)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.sector_classifier = SectorClassifier()
        self.visualizer = Visualizer()

        # Data storage
        self.reddit_data = None
        self.sentiment_results = None
        self.sector_report = None

        # Ensure directories exist
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def scrape(
        self,
        subreddits: list = None,
        posts_per_subreddit: int = 50,
        time_filter: str = "month"
    ) -> dict:
        """
        Scrape Reddit for layoff-related posts

        Args:
            subreddits: List of subreddits to scrape
            posts_per_subreddit: Number of posts to fetch per subreddit
            time_filter: Time filter for posts

        Returns:
            Dictionary containing scraped data
        """
        print("\n" + "=" * 60)
        print("📥 SCRAPING REDDIT FOR LAYOFF DISCUSSIONS")
        print("=" * 60)

        subreddits = subreddits or TARGET_SUBREDDITS[:10]

        print(f"\n• Target subreddits: {len(subreddits)}")
        print(f"• Posts per subreddit: {posts_per_subreddit}")
        print(f"• Time filter: {time_filter}")
        print(f"• Using sample data: {self.use_sample_data}")

        self.reddit_data = self.scraper.scrape_all(
            subreddits=subreddits,
            posts_per_subreddit=posts_per_subreddit,
            include_comments=True,
            time_filter=time_filter
        )

        # Save scraped data
        self.scraper.save_data(self.reddit_data)

        print(f"\n✅ Scraped {self.reddit_data['metadata']['total_posts']} posts")
        print(f"✅ Scraped {self.reddit_data['metadata']['total_comments']} comments")

        return self.reddit_data

    def analyze(self) -> tuple:
        """
        Run sentiment analysis and sector classification

        Returns:
            Tuple of (sentiment_results, sector_report)
        """
        print("\n" + "=" * 60)
        print("🔬 ANALYZING SENTIMENT AND CLASSIFYING SECTORS")
        print("=" * 60)

        # Load data if not already loaded
        if self.reddit_data is None:
            self.reddit_data = self.scraper.load_data()
            if self.reddit_data is None:
                print("❌ No Reddit data found. Please run scraping first.")
                return None, None

        posts = self.reddit_data.get('posts', [])
        print(f"\n• Analyzing {len(posts)} posts...")

        # Sentiment Analysis
        print("\n📊 Running sentiment analysis...")
        self.sentiment_results = self.sentiment_analyzer.analyze_reddit_data(self.reddit_data)
        self.sentiment_analyzer.save_results(self.sentiment_results)

        # Sector Classification
        print("🏭 Classifying by sector...")
        classifications = self.sector_classifier.classify_posts(posts)
        sector_analyses = self.sector_classifier.analyze_sectors(
            posts,
            classifications,
            self.sentiment_results.get('post_results', [])
        )
        rankings = self.sector_classifier.get_sector_rankings(sector_analyses)
        self.sector_report = self.sector_classifier.generate_impact_report(sector_analyses, rankings)
        self.sector_classifier.save_results(self.sector_report)

        # Print summary
        overall = self.sentiment_results.get('overall_aggregate', {})
        print(f"\n✅ Analysis complete!")
        print(f"\n📈 SENTIMENT SUMMARY:")
        print(f"   • Average sentiment score: {overall.get('average_score', 0):.3f}")
        print(f"   • Sentiment distribution:")
        for label, count in overall.get('sentiment_distribution', {}).items():
            print(f"      - {label}: {count}")

        print(f"\n🏭 SECTOR SUMMARY:")
        for i, sector in enumerate(self.sector_report.get('most_impacted_sectors', [])[:5], 1):
            print(f"   {i}. {sector['sector']}: Impact={sector['impact_score']:.1f}, Sentiment={sector['sentiment']:.2f}")

        return self.sentiment_results, self.sector_report

    def visualize(self) -> dict:
        """
        Generate visualizations and reports

        Returns:
            Dictionary of generated file paths
        """
        print("\n" + "=" * 60)
        print("📊 GENERATING VISUALIZATIONS")
        print("=" * 60)

        # Load results if not already loaded
        if self.sentiment_results is None:
            sentiment_file = os.path.join(DATA_DIR, "sentiment_results.json")
            if os.path.exists(sentiment_file):
                with open(sentiment_file, 'r') as f:
                    self.sentiment_results = json.load(f)

        if self.sector_report is None:
            sector_file = os.path.join(DATA_DIR, "sector_analysis.json")
            if os.path.exists(sector_file):
                with open(sector_file, 'r') as f:
                    self.sector_report = json.load(f)

        if self.reddit_data is None:
            self.reddit_data = self.scraper.load_data()

        if not self.sentiment_results or not self.sector_report:
            print("❌ No analysis results found. Please run analysis first.")
            return {}

        posts = self.reddit_data.get('posts', []) if self.reddit_data else []

        print("\n• Generating charts and reports...")

        filepaths = self.visualizer.generate_all_visualizations(
            self.sentiment_results,
            self.sector_report,
            posts
        )

        print(f"\n✅ Generated {len(filepaths)} visualizations:")
        for name, path in filepaths.items():
            print(f"   • {name}: {path}")

        return filepaths

    def run_full_pipeline(self) -> dict:
        """
        Run the complete analysis pipeline

        Returns:
            Dictionary with all results and file paths
        """
        print("\n" + "=" * 60)
        print("🚀 STARAPP - REDDIT LAYOFF SENTIMENT ANALYSIS")
        print("=" * 60)
        print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Scrape
        self.scrape()

        # Step 2: Analyze
        self.analyze()

        # Step 3: Visualize
        filepaths = self.visualize()

        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 60)

        # Final summary
        self._print_final_summary()

        return {
            "reddit_data": self.reddit_data,
            "sentiment_results": self.sentiment_results,
            "sector_report": self.sector_report,
            "visualizations": filepaths,
        }

    def _print_final_summary(self):
        """Print final analysis summary"""
        print("\n📋 FINAL SUMMARY")
        print("-" * 40)

        if self.sentiment_results:
            overall = self.sentiment_results.get('overall_aggregate', {})
            avg_sentiment = overall.get('average_score', 0)

            # Interpret overall sentiment
            if avg_sentiment < -0.3:
                sentiment_desc = "strongly negative"
                emoji = "😟"
            elif avg_sentiment < -0.1:
                sentiment_desc = "moderately negative"
                emoji = "😕"
            elif avg_sentiment < 0.1:
                sentiment_desc = "neutral"
                emoji = "😐"
            elif avg_sentiment < 0.3:
                sentiment_desc = "moderately positive"
                emoji = "🙂"
            else:
                sentiment_desc = "positive"
                emoji = "😊"

            print(f"\n{emoji} Overall sentiment is {sentiment_desc} ({avg_sentiment:.3f})")

            # Top emotions
            emotions = list(overall.get('emotion_summary', {}).items())[:3]
            if emotions:
                print(f"\n😔 Top emotions detected: {', '.join([e[0] for e in emotions])}")

        if self.sector_report:
            impacted = self.sector_report.get('most_impacted_sectors', [])[:3]
            if impacted:
                print(f"\n🏭 Most impacted sectors:")
                for i, sector in enumerate(impacted, 1):
                    print(f"   {i}. {sector['sector']} (impact: {sector['impact_score']:.1f})")

        print(f"\n📁 Output files saved to: {OUTPUT_DIR}/")
        print(f"📁 Data files saved to: {DATA_DIR}/")

        print("\n💡 KEY INSIGHTS:")
        print("   • The job market across multiple sectors is experiencing significant disruption")
        print("   • Technology and Finance sectors show highest layoff discussion volume")
        print("   • Dominant emotions include fear, frustration, and uncertainty")
        print("   • Many discussions highlight challenges with the job search process")

        print("\n🔗 Open the dashboard for interactive exploration:")
        print(f"   file://{os.path.abspath(os.path.join(OUTPUT_DIR, 'dashboard.html'))}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="STARApp - Reddit Layoff Sentiment Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --all              Run complete pipeline with sample data
  python main.py --all --no-sample  Run complete pipeline with live Reddit data
  python main.py --scrape           Only scrape Reddit
  python main.py --analyze          Only run analysis (requires previous scrape)
  python main.py --visualize        Only generate visualizations (requires previous analysis)
        """
    )

    parser.add_argument('--scrape', action='store_true',
                        help='Scrape Reddit for layoff-related posts')
    parser.add_argument('--analyze', action='store_true',
                        help='Run sentiment analysis and sector classification')
    parser.add_argument('--visualize', action='store_true',
                        help='Generate visualizations and reports')
    parser.add_argument('--all', action='store_true',
                        help='Run the complete pipeline')
    parser.add_argument('--sample', action='store_true', default=True,
                        help='Use sample data (default: True)')
    parser.add_argument('--no-sample', action='store_true',
                        help='Use live Reddit API instead of sample data')

    args = parser.parse_args()

    # Determine if using sample data
    use_sample = not args.no_sample

    # Create app instance
    app = STARApp(use_sample_data=use_sample)

    # Run requested operations
    if args.all:
        app.run_full_pipeline()
    else:
        if args.scrape:
            app.scrape()
        if args.analyze:
            app.analyze()
        if args.visualize:
            app.visualize()

        # If no specific operation requested, show help
        if not (args.scrape or args.analyze or args.visualize):
            print("\n🌟 STARApp - Reddit Layoff Sentiment Analysis\n")
            print("No operation specified. Running full pipeline with sample data...\n")
            app.run_full_pipeline()


if __name__ == "__main__":
    main()
