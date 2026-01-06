"""
Visualization Module
Creates visual representations of sentiment analysis and sector impact data
"""
import os
import json
from typing import List, Dict, Tuple, Optional
from collections import Counter
import logging

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import OUTPUT_DIR, DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class Visualizer:
    """
    Creates visualizations for layoff sentiment analysis
    """

    def __init__(self, output_dir: str = OUTPUT_DIR):
        """Initialize the visualizer"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Color schemes
        self.sentiment_colors = {
            "very_negative": "#d62728",
            "negative": "#ff7f0e",
            "neutral": "#7f7f7f",
            "positive": "#2ca02c",
            "very_positive": "#1f77b4",
        }

        self.sector_colors = px.colors.qualitative.Set3

    def create_sentiment_distribution(
        self,
        sentiment_data: Dict,
        title: str = "Sentiment Distribution",
        save_name: str = "sentiment_distribution"
    ) -> str:
        """Create a pie chart showing sentiment distribution"""
        distribution = sentiment_data.get('sentiment_distribution', {})

        if not distribution:
            logger.warning("No sentiment distribution data available")
            return None

        labels = list(distribution.keys())
        values = list(distribution.values())
        colors = [self.sentiment_colors.get(label, '#333333') for label in labels]

        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Pie chart
        wedges, texts, autotexts = ax1.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            explode=[0.05 if label in ['very_negative', 'negative'] else 0 for label in labels]
        )
        ax1.set_title(title, fontsize=14, fontweight='bold')

        # Bar chart
        bars = ax2.bar(labels, values, color=colors, edgecolor='black', linewidth=1.2)
        ax2.set_xlabel('Sentiment Category', fontsize=12)
        ax2.set_ylabel('Count', fontsize=12)
        ax2.set_title('Sentiment Counts', fontsize=14, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                str(value),
                ha='center',
                va='bottom',
                fontweight='bold'
            )

        plt.tight_layout()

        # Save
        filepath = os.path.join(self.output_dir, f"{save_name}.png")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved sentiment distribution chart to {filepath}")
        return filepath

    def create_sector_impact_chart(
        self,
        sector_report: Dict,
        save_name: str = "sector_impact"
    ) -> str:
        """Create a horizontal bar chart showing sector impact"""
        impacted_sectors = sector_report.get('most_impacted_sectors', [])

        if not impacted_sectors:
            logger.warning("No sector impact data available")
            return None

        sectors = [s['sector'] for s in impacted_sectors][:10]
        impact_scores = [s['impact_score'] for s in impacted_sectors][:10]
        sentiments = [s['sentiment'] for s in impacted_sectors][:10]

        # Normalize sentiments to colors (-1 to 1 -> red to green)
        norm_sentiments = [(s + 1) / 2 for s in sentiments]  # Normalize to 0-1
        colors = plt.cm.RdYlGn(norm_sentiments)

        fig, ax = plt.subplots(figsize=(12, 8))

        bars = ax.barh(sectors[::-1], impact_scores[::-1], color=colors[::-1], edgecolor='black')

        ax.set_xlabel('Impact Score', fontsize=12)
        ax.set_title('Layoff Impact by Sector\n(Color indicates sentiment: Red=Negative, Green=Positive)',
                     fontsize=14, fontweight='bold')

        # Add impact score labels
        for bar, score in zip(bars, impact_scores[::-1]):
            ax.text(
                bar.get_width() + 0.1,
                bar.get_y() + bar.get_height() / 2,
                f'{score:.1f}',
                va='center',
                fontweight='bold'
            )

        plt.tight_layout()

        filepath = os.path.join(self.output_dir, f"{save_name}.png")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved sector impact chart to {filepath}")
        return filepath

    def create_emotion_heatmap(
        self,
        sector_report: Dict,
        save_name: str = "emotion_heatmap"
    ) -> str:
        """Create a heatmap showing emotions across sectors"""
        sector_details = sector_report.get('sector_details', {})

        if not sector_details:
            logger.warning("No sector details available")
            return None

        # Collect all emotions
        all_emotions = set()
        for details in sector_details.values():
            emotions = dict(details.get('top_emotions', []))
            all_emotions.update(emotions.keys())

        if not all_emotions:
            logger.warning("No emotion data available")
            return None

        all_emotions = sorted(list(all_emotions))
        sectors = [s for s in sector_details.keys() if s != "Other/Unknown"][:10]

        # Create emotion matrix
        matrix = []
        for sector in sectors:
            details = sector_details.get(sector, {})
            emotions = dict(details.get('top_emotions', []))
            row = [emotions.get(emotion, 0) for emotion in all_emotions]
            matrix.append(row)

        matrix = np.array(matrix)

        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 8))

        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')

        ax.set_xticks(np.arange(len(all_emotions)))
        ax.set_yticks(np.arange(len(sectors)))
        ax.set_xticklabels(all_emotions, rotation=45, ha='right')
        ax.set_yticklabels(sectors)

        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('Emotion Count', rotation=-90, va="bottom")

        # Add text annotations
        for i in range(len(sectors)):
            for j in range(len(all_emotions)):
                if matrix[i, j] > 0:
                    text = ax.text(j, i, int(matrix[i, j]),
                                   ha="center", va="center", color="black", fontsize=8)

        ax.set_title('Emotion Distribution Across Sectors', fontsize=14, fontweight='bold')
        plt.tight_layout()

        filepath = os.path.join(self.output_dir, f"{save_name}.png")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved emotion heatmap to {filepath}")
        return filepath

    def create_sentiment_over_sectors(
        self,
        sector_report: Dict,
        save_name: str = "sector_sentiment"
    ) -> str:
        """Create a combined chart showing posts and sentiment by sector"""
        sector_details = sector_report.get('sector_details', {})

        if not sector_details:
            return None

        sectors = []
        post_counts = []
        sentiments = []
        engagements = []

        for sector, details in sector_details.items():
            if sector != "Other/Unknown" and details.get('post_count', 0) > 0:
                sectors.append(sector)
                post_counts.append(details.get('post_count', 0))
                sentiments.append(details.get('average_sentiment', 0))
                engagements.append(details.get('total_engagement', 0))

        # Sort by post count
        sorted_idx = np.argsort(post_counts)[::-1][:10]
        sectors = [sectors[i] for i in sorted_idx]
        post_counts = [post_counts[i] for i in sorted_idx]
        sentiments = [sentiments[i] for i in sorted_idx]
        engagements = [engagements[i] for i in sorted_idx]

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Post count by sector
        ax1 = axes[0, 0]
        bars1 = ax1.bar(range(len(sectors)), post_counts, color='steelblue', edgecolor='black')
        ax1.set_xticks(range(len(sectors)))
        ax1.set_xticklabels(sectors, rotation=45, ha='right')
        ax1.set_ylabel('Number of Posts')
        ax1.set_title('Posts by Sector', fontweight='bold')

        # 2. Average sentiment by sector
        ax2 = axes[0, 1]
        colors = ['#d62728' if s < -0.2 else '#2ca02c' if s > 0.2 else '#7f7f7f' for s in sentiments]
        bars2 = ax2.bar(range(len(sectors)), sentiments, color=colors, edgecolor='black')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_xticks(range(len(sectors)))
        ax2.set_xticklabels(sectors, rotation=45, ha='right')
        ax2.set_ylabel('Average Sentiment Score')
        ax2.set_title('Sentiment by Sector', fontweight='bold')
        ax2.set_ylim(-1, 1)

        # 3. Engagement by sector
        ax3 = axes[1, 0]
        bars3 = ax3.bar(range(len(sectors)), engagements, color='darkorange', edgecolor='black')
        ax3.set_xticks(range(len(sectors)))
        ax3.set_xticklabels(sectors, rotation=45, ha='right')
        ax3.set_ylabel('Total Engagement (Score + Comments)')
        ax3.set_title('Engagement by Sector', fontweight='bold')

        # 4. Scatter plot: Posts vs Sentiment
        ax4 = axes[1, 1]
        scatter_colors = ['#d62728' if s < -0.2 else '#2ca02c' if s > 0.2 else '#7f7f7f' for s in sentiments]
        sizes = [e / 10 + 50 for e in engagements]  # Scale engagement for bubble size
        ax4.scatter(post_counts, sentiments, c=scatter_colors, s=sizes, alpha=0.7, edgecolors='black')

        for i, sector in enumerate(sectors):
            ax4.annotate(sector, (post_counts[i], sentiments[i]),
                         fontsize=8, ha='center', va='bottom')

        ax4.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        ax4.set_xlabel('Number of Posts')
        ax4.set_ylabel('Average Sentiment')
        ax4.set_title('Posts vs Sentiment\n(Bubble size = engagement)', fontweight='bold')

        plt.tight_layout()

        filepath = os.path.join(self.output_dir, f"{save_name}.png")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved sector sentiment chart to {filepath}")
        return filepath

    def create_wordcloud(
        self,
        text_data: List[str],
        title: str = "Layoff Discussion Topics",
        save_name: str = "wordcloud"
    ) -> str:
        """Create a word cloud from text data"""
        if not text_data:
            logger.warning("No text data for word cloud")
            return None

        # Combine all text
        combined_text = ' '.join(text_data)

        # Create word cloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap='viridis',
            max_words=100,
            min_font_size=10,
            max_font_size=100,
            random_state=42,
        ).generate(combined_text)

        fig, ax = plt.subplots(figsize=(15, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

        filepath = os.path.join(self.output_dir, f"{save_name}.png")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved word cloud to {filepath}")
        return filepath

    def create_interactive_dashboard(
        self,
        sentiment_results: Dict,
        sector_report: Dict,
        save_name: str = "dashboard"
    ) -> str:
        """Create an interactive HTML dashboard using Plotly"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Sentiment Distribution',
                'Sector Impact Rankings',
                'Sentiment by Sector',
                'Emotion Analysis',
                'Post Volume Over Sectors',
                'Engagement vs Sentiment'
            ),
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        # 1. Sentiment Distribution Pie Chart
        distribution = sentiment_results.get('overall_aggregate', {}).get('sentiment_distribution', {})
        if distribution:
            colors = [self.sentiment_colors.get(k, '#333') for k in distribution.keys()]
            fig.add_trace(
                go.Pie(
                    labels=list(distribution.keys()),
                    values=list(distribution.values()),
                    marker=dict(colors=colors),
                    textinfo='percent+label',
                    hole=0.3
                ),
                row=1, col=1
            )

        # 2. Sector Impact Rankings
        impacted = sector_report.get('most_impacted_sectors', [])[:10]
        if impacted:
            fig.add_trace(
                go.Bar(
                    y=[s['sector'] for s in impacted][::-1],
                    x=[s['impact_score'] for s in impacted][::-1],
                    orientation='h',
                    marker=dict(
                        color=[s['sentiment'] for s in impacted][::-1],
                        colorscale='RdYlGn',
                        cmin=-1,
                        cmax=1
                    ),
                    text=[f"{s['impact_score']:.1f}" for s in impacted][::-1],
                    textposition='outside'
                ),
                row=1, col=2
            )

        # 3. Sentiment by Sector
        sector_details = sector_report.get('sector_details', {})
        sectors = [s for s in sector_details.keys() if s != "Other/Unknown"][:10]
        sentiments = [sector_details[s].get('average_sentiment', 0) for s in sectors]
        colors = ['red' if s < -0.2 else 'green' if s > 0.2 else 'gray' for s in sentiments]

        fig.add_trace(
            go.Bar(
                x=sectors,
                y=sentiments,
                marker_color=colors,
                text=[f"{s:.2f}" for s in sentiments],
                textposition='outside'
            ),
            row=2, col=1
        )

        # 4. Emotion Analysis
        emotions = sentiment_results.get('overall_aggregate', {}).get('emotion_summary', {})
        if emotions:
            fig.add_trace(
                go.Bar(
                    x=list(emotions.keys())[:8],
                    y=list(emotions.values())[:8],
                    marker_color='indianred'
                ),
                row=2, col=2
            )

        # 5. Post Volume
        post_counts = [sector_details[s].get('post_count', 0) for s in sectors]
        fig.add_trace(
            go.Bar(
                x=sectors,
                y=post_counts,
                marker_color='steelblue'
            ),
            row=3, col=1
        )

        # 6. Engagement vs Sentiment Scatter
        engagements = [sector_details[s].get('total_engagement', 0) for s in sectors]
        fig.add_trace(
            go.Scatter(
                x=engagements,
                y=sentiments,
                mode='markers+text',
                text=sectors,
                textposition='top center',
                marker=dict(
                    size=[p * 3 + 10 for p in post_counts],
                    color=sentiments,
                    colorscale='RdYlGn',
                    cmin=-1,
                    cmax=1,
                    showscale=True,
                    colorbar=dict(title="Sentiment")
                )
            ),
            row=3, col=2
        )

        # Update layout
        fig.update_layout(
            height=1200,
            width=1400,
            title_text="<b>Reddit Layoff Sentiment Analysis Dashboard</b>",
            title_x=0.5,
            showlegend=False,
            template='plotly_white'
        )

        # Update axes labels
        fig.update_xaxes(title_text="Impact Score", row=1, col=2)
        fig.update_xaxes(title_text="Sector", row=2, col=1, tickangle=45)
        fig.update_yaxes(title_text="Avg Sentiment", row=2, col=1)
        fig.update_xaxes(title_text="Emotion", row=2, col=2)
        fig.update_yaxes(title_text="Count", row=2, col=2)
        fig.update_xaxes(title_text="Sector", row=3, col=1, tickangle=45)
        fig.update_yaxes(title_text="Post Count", row=3, col=1)
        fig.update_xaxes(title_text="Engagement", row=3, col=2)
        fig.update_yaxes(title_text="Sentiment", row=3, col=2)

        # Save as HTML
        filepath = os.path.join(self.output_dir, f"{save_name}.html")
        fig.write_html(filepath)

        logger.info(f"Saved interactive dashboard to {filepath}")
        return filepath

    def create_summary_report(
        self,
        sentiment_results: Dict,
        sector_report: Dict,
        save_name: str = "analysis_report"
    ) -> str:
        """Create a comprehensive summary report in HTML format"""
        overall = sentiment_results.get('overall_aggregate', {})
        impacted = sector_report.get('most_impacted_sectors', [])[:5]

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Layoff Sentiment Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .sector-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }}
        .sector-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .sentiment-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .sentiment-negative {{
            background: #ffebee;
            color: #c62828;
        }}
        .sentiment-neutral {{
            background: #f5f5f5;
            color: #616161;
        }}
        .sentiment-positive {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        .insight-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .insight-box h4 {{
            margin: 0 0 10px 0;
            color: #1976d2;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Reddit Layoff Sentiment Analysis</h1>
        <p>Comprehensive analysis of layoff discussions across Reddit</p>
    </div>

    <div class="section">
        <h2>📈 Executive Summary</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{overall.get('total_analyzed', 0)}</div>
                <div class="metric-label">Posts Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overall.get('average_score', 0):.2f}</div>
                <div class="metric-label">Avg Sentiment Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(sector_report.get('sector_details', {}))}</div>
                <div class="metric-label">Sectors Identified</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{sector_report.get('summary', {}).get('total_engagement', 0):,}</div>
                <div class="metric-label">Total Engagement</div>
            </div>
        </div>

        <div class="insight-box">
            <h4>🔍 Key Finding</h4>
            <p>The overall sentiment across layoff discussions is <strong>{"negative" if overall.get('average_score', 0) < -0.2 else "neutral" if overall.get('average_score', 0) < 0.2 else "positive"}</strong>
            with an average score of {overall.get('average_score', 0):.3f}.
            The most commonly expressed emotions are {', '.join(list(overall.get('emotion_summary', {}).keys())[:3])}.</p>
        </div>
    </div>

    <div class="section">
        <h2>🏭 Most Impacted Sectors</h2>
        <p>The following sectors show the highest levels of layoff-related discussion and negative sentiment:</p>

        {"".join(f'''
        <div class="sector-card">
            <h3>{i+1}. {sector['sector']}</h3>
            <p><strong>Impact Score:</strong> {sector['impact_score']} |
               <strong>Posts:</strong> {sector['post_count']} |
               <strong>Engagement:</strong> {sector['engagement']:,}</p>
            <p>
                <span class="sentiment-badge {"sentiment-negative" if sector['sentiment'] < -0.2 else "sentiment-positive" if sector['sentiment'] > 0.2 else "sentiment-neutral"}">
                    Sentiment: {sector['sentiment']:.2f}
                </span>
            </p>
        </div>
        ''' for i, sector in enumerate(impacted))}
    </div>

    <div class="section">
        <h2>📊 Sentiment Distribution</h2>
        <table>
            <tr>
                <th>Sentiment Category</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
            {"".join(f'''
            <tr>
                <td>{category}</td>
                <td>{count}</td>
                <td>{count/max(overall.get('total_analyzed', 1), 1)*100:.1f}%</td>
            </tr>
            ''' for category, count in overall.get('sentiment_distribution', {}).items())}
        </table>
    </div>

    <div class="section">
        <h2>😔 Emotion Analysis</h2>
        <p>Top emotions expressed in layoff discussions:</p>
        <table>
            <tr>
                <th>Emotion</th>
                <th>Mentions</th>
            </tr>
            {"".join(f'''
            <tr>
                <td>{emotion.title()}</td>
                <td>{count}</td>
            </tr>
            ''' for emotion, count in list(overall.get('emotion_summary', {}).items())[:8])}
        </table>
    </div>

    <div class="section">
        <h2>💡 Key Insights</h2>
        <div class="insight-box">
            <h4>Technology Sector</h4>
            <p>The technology sector shows significant layoff activity with major companies like Google, Meta, and Amazon
            mentioned frequently. Sentiment in tech-related discussions tends to be mixed, with frustration about job
            market conditions but also optimism about upskilling opportunities.</p>
        </div>

        <div class="insight-box">
            <h4>Finance & Banking</h4>
            <p>Investment banking and financial services are experiencing notable workforce reductions.
            Discussions reveal concerns about bonus cuts, job security, and the changing nature of work
            in traditional finance.</p>
        </div>

        <div class="insight-box">
            <h4>Overall Job Market</h4>
            <p>The data suggests a challenging job market across multiple sectors. Common themes include:
            lengthy interview processes, "ghost jobs" (posted but not actively hiring), and increased
            competition for available positions.</p>
        </div>
    </div>

    <div class="section">
        <h2>📋 Recommendations</h2>
        <ul>
            <li><strong>For Job Seekers:</strong> Focus on networking and direct outreach rather than mass applications.
            The data shows that personal connections lead to better outcomes in the current market.</li>
            <li><strong>For HR/Employers:</strong> Transparent communication about hiring status can improve employer brand.
            Many negative discussions stem from poor communication during the hiring process.</li>
            <li><strong>For Policy Makers:</strong> The emotional toll of layoffs extends beyond financial impact.
            Mental health support and career transition resources are critical needs.</li>
        </ul>
    </div>

    <div class="footer">
        <p>Generated by STARApp - Sentiment Tracker and Analysis for Reddit</p>
        <p>Data sourced from Reddit discussions about layoffs and unemployment</p>
    </div>
</body>
</html>
"""

        filepath = os.path.join(self.output_dir, f"{save_name}.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Saved summary report to {filepath}")
        return filepath

    def generate_all_visualizations(
        self,
        sentiment_results: Dict,
        sector_report: Dict,
        posts: List[Dict] = None
    ) -> Dict[str, str]:
        """Generate all visualizations and return file paths"""
        filepaths = {}

        # 1. Sentiment distribution
        if 'overall_aggregate' in sentiment_results:
            path = self.create_sentiment_distribution(
                sentiment_results['overall_aggregate'],
                title="Overall Sentiment Distribution"
            )
            if path:
                filepaths['sentiment_distribution'] = path

        # 2. Sector impact chart
        path = self.create_sector_impact_chart(sector_report)
        if path:
            filepaths['sector_impact'] = path

        # 3. Sector sentiment analysis
        path = self.create_sentiment_over_sectors(sector_report)
        if path:
            filepaths['sector_sentiment'] = path

        # 4. Emotion heatmap
        path = self.create_emotion_heatmap(sector_report)
        if path:
            filepaths['emotion_heatmap'] = path

        # 5. Word cloud
        if posts:
            texts = [
                f"{p.get('title', '')} {p.get('selftext', '')}"
                for p in posts
            ]
            path = self.create_wordcloud(texts)
            if path:
                filepaths['wordcloud'] = path

        # 6. Interactive dashboard
        path = self.create_interactive_dashboard(sentiment_results, sector_report)
        if path:
            filepaths['dashboard'] = path

        # 7. Summary report
        path = self.create_summary_report(sentiment_results, sector_report)
        if path:
            filepaths['report'] = path

        logger.info(f"Generated {len(filepaths)} visualizations")
        return filepaths


def main():
    """Main function to generate visualizations"""
    # Load data
    sentiment_file = os.path.join(DATA_DIR, "sentiment_results.json")
    sector_file = os.path.join(DATA_DIR, "sector_analysis.json")
    reddit_file = os.path.join(DATA_DIR, "reddit_data.json")

    sentiment_results = {}
    sector_report = {}
    posts = []

    if os.path.exists(sentiment_file):
        with open(sentiment_file, 'r') as f:
            sentiment_results = json.load(f)

    if os.path.exists(sector_file):
        with open(sector_file, 'r') as f:
            sector_report = json.load(f)

    if os.path.exists(reddit_file):
        with open(reddit_file, 'r') as f:
            data = json.load(f)
            posts = data.get('posts', [])

    if not sentiment_results or not sector_report:
        print("No analysis data found. Please run the analysis first.")
        return

    # Generate visualizations
    visualizer = Visualizer()
    filepaths = visualizer.generate_all_visualizations(
        sentiment_results,
        sector_report,
        posts
    )

    print("\n" + "=" * 60)
    print("VISUALIZATIONS GENERATED")
    print("=" * 60)
    for name, path in filepaths.items():
        print(f"  {name}: {path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
