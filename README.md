# STARApp - Sentiment Tracker and Analysis for Reddit

## 📊 Reddit Layoff Sentiment Analysis Tool

STARApp is a comprehensive Python application that scrapes Reddit for discussions about layoffs, unemployment, and underemployment, performs sentiment analysis, classifies posts by industry sector, and generates visual representations to analyze which sectors are most impacted.

## 🌟 Features

- **Reddit Scraping**: Automatically scrapes layoff-related discussions from multiple subreddits
- **Sentiment Analysis**: Uses VADER and TextBlob for multi-method sentiment analysis
- **Sector Classification**: Classifies posts by industry sector (Tech, Finance, Healthcare, etc.)
- **Emotion Detection**: Identifies emotions like fear, anger, frustration, hope
- **Impact Analysis**: Ranks sectors by layoff impact using composite scoring
- **Rich Visualizations**:
  - Interactive HTML dashboard
  - Sentiment distribution charts
  - Sector impact rankings
  - Emotion heatmaps
  - Word clouds
  - Comprehensive HTML reports

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/STARApp.git
cd STARApp
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Set up Reddit API credentials:
```bash
cp .env.example .env
# Edit .env with your Reddit API credentials
```

### Running the Application

**Run with sample data (no Reddit API required):**
```bash
python main.py --all
```

**Run with live Reddit data:**
```bash
python main.py --all --no-sample
```

**Run individual steps:**
```bash
# Only scrape Reddit
python main.py --scrape

# Only run analysis
python main.py --analyze

# Only generate visualizations
python main.py --visualize
```

## 📁 Project Structure

```
STARApp/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration settings
├── src/
│   ├── __init__.py
│   ├── reddit_scraper.py  # Reddit scraping module
│   ├── sentiment_analyzer.py  # Sentiment analysis engine
│   ├── sector_classifier.py   # Sector classification
│   └── visualizer.py      # Visualization generation
├── data/                  # Scraped and processed data
│   ├── reddit_data.json
│   ├── sentiment_results.json
│   └── sector_analysis.json
├── output/                # Generated visualizations
│   ├── dashboard.html
│   ├── analysis_report.html
│   ├── sentiment_distribution.png
│   ├── sector_impact.png
│   └── ...
└── templates/             # HTML templates
```

## 📊 Output

After running the analysis, you'll find the following outputs:

### Data Files (in `data/`)
- `reddit_data.json` - Raw scraped Reddit data
- `sentiment_results.json` - Sentiment analysis results
- `sector_analysis.json` - Sector classification and impact analysis

### Visualizations (in `output/`)
- `dashboard.html` - Interactive Plotly dashboard
- `analysis_report.html` - Comprehensive HTML report
- `sentiment_distribution.png` - Pie/bar chart of sentiment distribution
- `sector_impact.png` - Horizontal bar chart of sector impact
- `sector_sentiment.png` - Multi-panel sector analysis
- `emotion_heatmap.png` - Heatmap of emotions across sectors
- `wordcloud.png` - Word cloud of discussion topics

## 🏭 Analyzed Sectors

The application classifies discussions into the following sectors:
- Technology
- Finance & Banking
- Healthcare
- Retail & E-commerce
- Manufacturing
- Media & Entertainment
- Education
- Real Estate & Construction
- Hospitality & Travel
- Consulting & Professional Services
- Government & Public Sector
- Energy & Utilities
- Legal

## 🔧 Configuration

Edit `config/settings.py` to customize:

- **TARGET_SUBREDDITS**: List of subreddits to scrape
- **SEARCH_KEYWORDS**: Keywords to identify layoff-related content
- **SECTOR_KEYWORDS**: Keywords for sector classification
- **SENTIMENT_THRESHOLDS**: Thresholds for sentiment categories
- **MAX_POSTS_PER_SUBREDDIT**: Number of posts to scrape per subreddit

## 📈 Sample Output

### Sentiment Distribution
```
very_negative: 25%
negative: 35%
neutral: 20%
positive: 15%
very_positive: 5%
```

### Most Impacted Sectors
1. Technology (Impact: 8.5)
2. Finance & Banking (Impact: 7.2)
3. Media & Entertainment (Impact: 6.1)
4. Consulting & Professional Services (Impact: 5.8)
5. Retail & E-commerce (Impact: 5.3)

### Top Emotions Detected
- Fear: 45 mentions
- Frustration: 38 mentions
- Uncertainty: 32 mentions
- Stress: 28 mentions
- Anger: 24 mentions

## 🔐 Reddit API Setup (Optional)

To use live Reddit data instead of sample data:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the details:
   - Name: LayoffSentimentAnalyzer
   - Type: script
   - Redirect URI: http://localhost:8080
4. Copy the client ID and secret to your `.env` file

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. The sentiment analysis and sector classifications are automated and may not always be accurate. The sample data is simulated and does not represent real Reddit posts.

## 🙏 Acknowledgments

- [PRAW](https://praw.readthedocs.io/) - Python Reddit API Wrapper
- [VADER Sentiment](https://github.com/cjhutto/vaderSentiment) - Sentiment Analysis
- [TextBlob](https://textblob.readthedocs.io/) - Natural Language Processing
- [Plotly](https://plotly.com/python/) - Interactive Visualizations
- [Seaborn](https://seaborn.pydata.org/) - Statistical Visualizations
