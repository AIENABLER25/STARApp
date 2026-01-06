"""
Reddit Scraper Module
Scrapes Reddit for layoff, unemployment, and underemployment discussions
"""
import praw
import prawcore
import time
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass, asdict
from tqdm import tqdm
import logging

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    REDDIT_CONFIG,
    TARGET_SUBREDDITS,
    SEARCH_KEYWORDS,
    MAX_POSTS_PER_SUBREDDIT,
    MAX_COMMENTS_PER_POST,
    RATE_LIMIT_DELAY,
    DATA_DIR,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RedditPost:
    """Data class for Reddit post information"""
    id: str
    subreddit: str
    title: str
    selftext: str
    author: str
    created_utc: float
    score: int
    upvote_ratio: float
    num_comments: int
    url: str
    permalink: str
    flair: Optional[str]
    is_self: bool


@dataclass
class RedditComment:
    """Data class for Reddit comment information"""
    id: str
    post_id: str
    subreddit: str
    body: str
    author: str
    created_utc: float
    score: int
    parent_id: str
    is_submitter: bool


class RedditScraper:
    """
    Scrapes Reddit for layoff and unemployment-related discussions
    """

    def __init__(self, use_sample_data: bool = False):
        """
        Initialize the Reddit scraper

        Args:
            use_sample_data: If True, use sample data instead of live API
        """
        self.use_sample_data = use_sample_data
        self.reddit = None

        if not use_sample_data:
            self._init_reddit_client()

    def _init_reddit_client(self):
        """Initialize the Reddit API client"""
        try:
            if REDDIT_CONFIG["client_id"] and REDDIT_CONFIG["client_secret"]:
                self.reddit = praw.Reddit(
                    client_id=REDDIT_CONFIG["client_id"],
                    client_secret=REDDIT_CONFIG["client_secret"],
                    user_agent=REDDIT_CONFIG["user_agent"],
                )
                # Test connection
                self.reddit.user.me()
                logger.info("Successfully connected to Reddit API")
            else:
                logger.warning("Reddit API credentials not found. Using read-only mode.")
                self.reddit = praw.Reddit(
                    client_id=REDDIT_CONFIG.get("client_id", "dummy"),
                    client_secret=REDDIT_CONFIG.get("client_secret", "dummy"),
                    user_agent=REDDIT_CONFIG["user_agent"],
                )
        except prawcore.exceptions.ResponseException as e:
            logger.warning(f"Reddit API authentication failed: {e}. Using sample data.")
            self.use_sample_data = True
        except Exception as e:
            logger.warning(f"Could not connect to Reddit API: {e}. Using sample data.")
            self.use_sample_data = True

    def _matches_keywords(self, text: str) -> bool:
        """Check if text contains layoff-related keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in SEARCH_KEYWORDS)

    def scrape_subreddit(
        self,
        subreddit_name: str,
        limit: int = MAX_POSTS_PER_SUBREDDIT,
        time_filter: str = "month"
    ) -> List[RedditPost]:
        """
        Scrape posts from a specific subreddit

        Args:
            subreddit_name: Name of the subreddit to scrape
            limit: Maximum number of posts to retrieve
            time_filter: Time filter for top posts (hour, day, week, month, year, all)

        Returns:
            List of RedditPost objects
        """
        if self.use_sample_data:
            return self._get_sample_posts(subreddit_name)

        posts = []
        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Get top posts and search for layoff-related content
            for post in tqdm(
                subreddit.top(time_filter=time_filter, limit=limit),
                desc=f"Scraping r/{subreddit_name}",
                total=limit
            ):
                if self._matches_keywords(post.title) or self._matches_keywords(post.selftext):
                    posts.append(self._post_to_dataclass(post))
                time.sleep(RATE_LIMIT_DELAY / 10)  # Rate limiting

            # Also search for specific keywords
            for keyword in SEARCH_KEYWORDS[:5]:  # Limit to avoid rate limiting
                try:
                    for post in subreddit.search(keyword, time_filter=time_filter, limit=limit//5):
                        if not any(p.id == post.id for p in posts):
                            posts.append(self._post_to_dataclass(post))
                        time.sleep(RATE_LIMIT_DELAY / 10)
                except Exception as e:
                    logger.warning(f"Search error for '{keyword}' in r/{subreddit_name}: {e}")

        except prawcore.exceptions.Forbidden:
            logger.warning(f"Access to r/{subreddit_name} is forbidden (quarantined/private)")
        except prawcore.exceptions.NotFound:
            logger.warning(f"Subreddit r/{subreddit_name} not found")
        except Exception as e:
            logger.error(f"Error scraping r/{subreddit_name}: {e}")

        return posts

    def _post_to_dataclass(self, post) -> RedditPost:
        """Convert PRAW post object to RedditPost dataclass"""
        return RedditPost(
            id=post.id,
            subreddit=str(post.subreddit),
            title=post.title,
            selftext=post.selftext or "",
            author=str(post.author) if post.author else "[deleted]",
            created_utc=post.created_utc,
            score=post.score,
            upvote_ratio=post.upvote_ratio,
            num_comments=post.num_comments,
            url=post.url,
            permalink=post.permalink,
            flair=post.link_flair_text,
            is_self=post.is_self,
        )

    def scrape_comments(
        self,
        post_id: str,
        limit: int = MAX_COMMENTS_PER_POST
    ) -> List[RedditComment]:
        """
        Scrape comments from a specific post

        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to retrieve

        Returns:
            List of RedditComment objects
        """
        if self.use_sample_data:
            return self._get_sample_comments(post_id)

        comments = []
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "more comments" links

            for comment in submission.comments.list()[:limit]:
                if hasattr(comment, 'body'):
                    comments.append(RedditComment(
                        id=comment.id,
                        post_id=post_id,
                        subreddit=str(submission.subreddit),
                        body=comment.body,
                        author=str(comment.author) if comment.author else "[deleted]",
                        created_utc=comment.created_utc,
                        score=comment.score,
                        parent_id=comment.parent_id,
                        is_submitter=comment.is_submitter,
                    ))
                time.sleep(RATE_LIMIT_DELAY / 20)

        except Exception as e:
            logger.error(f"Error scraping comments for post {post_id}: {e}")

        return comments

    def scrape_all(
        self,
        subreddits: List[str] = None,
        posts_per_subreddit: int = MAX_POSTS_PER_SUBREDDIT,
        include_comments: bool = True,
        time_filter: str = "month"
    ) -> Dict:
        """
        Scrape all target subreddits for layoff-related content

        Args:
            subreddits: List of subreddits to scrape (defaults to TARGET_SUBREDDITS)
            posts_per_subreddit: Max posts per subreddit
            include_comments: Whether to scrape comments
            time_filter: Time filter for posts

        Returns:
            Dictionary containing posts and comments
        """
        subreddits = subreddits or TARGET_SUBREDDITS
        all_posts = []
        all_comments = []

        logger.info(f"Starting scrape of {len(subreddits)} subreddits...")

        for subreddit in subreddits:
            posts = self.scrape_subreddit(subreddit, posts_per_subreddit, time_filter)
            all_posts.extend(posts)

            if include_comments:
                for post in posts[:10]:  # Limit comments to top 10 posts per subreddit
                    comments = self.scrape_comments(post.id)
                    all_comments.extend(comments)

            time.sleep(RATE_LIMIT_DELAY)

        logger.info(f"Scraped {len(all_posts)} posts and {len(all_comments)} comments")

        return {
            "posts": [asdict(p) for p in all_posts],
            "comments": [asdict(c) for c in all_comments],
            "metadata": {
                "scraped_at": datetime.now().isoformat(),
                "subreddits": subreddits,
                "total_posts": len(all_posts),
                "total_comments": len(all_comments),
            }
        }

    def save_data(self, data: Dict, filename: str = "reddit_data.json"):
        """Save scraped data to JSON file"""
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Data saved to {filepath}")
        return filepath

    def load_data(self, filename: str = "reddit_data.json") -> Dict:
        """Load previously scraped data from JSON file"""
        filepath = os.path.join(DATA_DIR, filename)

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"No data file found at {filepath}")
            return None

    def _get_sample_posts(self, subreddit_name: str = None) -> List[RedditPost]:
        """Generate sample posts for testing without API access"""
        sample_posts = [
            RedditPost(
                id="sample1",
                subreddit="layoffs",
                title="Just got laid off from Google after 5 years - Need advice",
                selftext="I was part of the recent tech layoffs at Google. 5 years of service and got the news via email. Feeling lost and uncertain about the future. The severance is decent but the job market seems tough. Anyone else going through this? How are you coping? I'm a senior software engineer with experience in distributed systems.",
                author="tech_worker_123",
                created_utc=datetime.now().timestamp() - 86400,
                score=2547,
                upvote_ratio=0.94,
                num_comments=384,
                url="https://reddit.com/r/layoffs/sample1",
                permalink="/r/layoffs/sample1",
                flair="Tech",
                is_self=True,
            ),
            RedditPost(
                id="sample2",
                subreddit="cscareerquestions",
                title="Meta just announced another round of layoffs - 10,000 more jobs",
                selftext="Just saw the news. Meta is cutting another 10,000 jobs. This is getting scary. I work in tech and even though I haven't been affected yet, the anxiety is real. How are other tech workers preparing for potential layoffs? Should I start interviewing now?",
                author="anxious_dev",
                created_utc=datetime.now().timestamp() - 172800,
                score=3891,
                upvote_ratio=0.91,
                num_comments=612,
                url="https://reddit.com/r/cscareerquestions/sample2",
                permalink="/r/cscareerquestions/sample2",
                flair="Career Advice",
                is_self=True,
            ),
            RedditPost(
                id="sample3",
                subreddit="nursing",
                title="Hospital layoffs hitting hard - Anyone else seeing this?",
                selftext="Our hospital just announced they're laying off 200 nurses due to 'budget constraints'. This is after we worked through the pandemic. The healthcare industry feels so unstable right now. ICU nurses, ER nurses, even floor nurses are being let go. The remaining staff is expected to pick up the slack. Morale is at an all-time low.",
                author="burned_out_rn",
                created_utc=datetime.now().timestamp() - 259200,
                score=1823,
                upvote_ratio=0.96,
                num_comments=445,
                url="https://reddit.com/r/nursing/sample3",
                permalink="/r/nursing/sample3",
                flair="Rant",
                is_self=True,
            ),
            RedditPost(
                id="sample4",
                subreddit="finance",
                title="Goldman Sachs and Morgan Stanley layoffs - Investment banking bloodbath",
                selftext="The investment banking sector is seeing massive cuts. Goldman laid off 3,200 people, Morgan Stanley around 3,000. JPMorgan is also rumored to be planning cuts. As a junior analyst, I'm terrified. Bonuses are down, hours are still brutal, and now job security is gone too. Anyone else in IB dealing with this?",
                author="ibanker_throwaway",
                created_utc=datetime.now().timestamp() - 345600,
                score=1456,
                upvote_ratio=0.89,
                num_comments=298,
                url="https://reddit.com/r/finance/sample4",
                permalink="/r/finance/sample4",
                flair="Career",
                is_self=True,
            ),
            RedditPost(
                id="sample5",
                subreddit="recruitinghell",
                title="Applied to 500 jobs after layoff, only 3 interviews. The market is brutal.",
                selftext="I was laid off from Amazon 4 months ago. Senior software engineer with 8 years of experience. Applied to over 500 positions. Got 3 phone screens, 1 onsite, and no offers. Companies are posting ghost jobs. The interview process takes months. I've never seen it this bad. My unemployment runs out in 2 months.",
                author="job_search_hell",
                created_utc=datetime.now().timestamp() - 432000,
                score=4521,
                upvote_ratio=0.97,
                num_comments=892,
                url="https://reddit.com/r/recruitinghell/sample5",
                permalink="/r/recruitinghell/sample5",
                flair="Unemployment",
                is_self=True,
            ),
            RedditPost(
                id="sample6",
                subreddit="teachers",
                title="School district just announced they're eliminating 150 teaching positions",
                selftext="Budget cuts are hitting education hard. Our district just announced they're eliminating 150 teaching positions. Special education, arts, and physical education are being hit the hardest. Class sizes are going to balloon. I've been teaching for 15 years and never seen cuts this severe. Many young teachers are being let go.",
                author="educator_in_crisis",
                created_utc=datetime.now().timestamp() - 518400,
                score=2134,
                upvote_ratio=0.93,
                num_comments=367,
                url="https://reddit.com/r/teachers/sample6",
                permalink="/r/teachers/sample6",
                flair="Policy",
                is_self=True,
            ),
            RedditPost(
                id="sample7",
                subreddit="retail",
                title="Retail apocalypse continues - Major store closing 500 locations",
                selftext="Another major retailer announced they're closing 500 stores nationwide. Thousands of retail workers will be unemployed. I work at one of the closing locations. No severance for hourly workers, just a 'thanks for your service'. Trying to find another retail job but everyone is cutting back.",
                author="retail_survivor",
                created_utc=datetime.now().timestamp() - 604800,
                score=1678,
                upvote_ratio=0.91,
                num_comments=234,
                url="https://reddit.com/r/retail/sample7",
                permalink="/r/retail/sample7",
                flair="News",
                is_self=True,
            ),
            RedditPost(
                id="sample8",
                subreddit="accounting",
                title="Big 4 layoffs spreading - Deloitte and EY cutting staff",
                selftext="The Big 4 are finally feeling the pressure. Deloitte just let go of 1,200 people, EY around 3,000. Even partners aren't safe. Advisory and consulting are getting hit hardest. As a senior associate at PwC, I'm updating my resume. The promised stability of accounting is a myth. Anyone else looking to leave public?",
                author="big4_burnout",
                created_utc=datetime.now().timestamp() - 691200,
                score=1987,
                upvote_ratio=0.88,
                num_comments=445,
                url="https://reddit.com/r/accounting/sample8",
                permalink="/r/accounting/sample8",
                flair="Big 4",
                is_self=True,
            ),
            RedditPost(
                id="sample9",
                subreddit="marketing",
                title="Marketing department gutted - CMO to intern, everyone let go",
                selftext="Our company just fired the entire marketing department - from CMO down to the interns. They're 'pivoting to AI-driven marketing'. 45 people lost their jobs. I had 10 years of experience in digital marketing and brand management. Now competing with thousands of other laid-off marketers. The creative industry is struggling.",
                author="former_marketer",
                created_utc=datetime.now().timestamp() - 777600,
                score=2345,
                upvote_ratio=0.94,
                num_comments=512,
                url="https://reddit.com/r/marketing/sample9",
                permalink="/r/marketing/sample9",
                flair="Discussion",
                is_self=True,
            ),
            RedditPost(
                id="sample10",
                subreddit="antiwork",
                title="Company made record profits then laid off 20% of workforce - capitalism is broken",
                selftext="My company just announced record quarterly profits of $2.8 billion. Same week, they laid off 20% of the workforce - over 5,000 people. CEO got a $45 million bonus. Executives flew in on private jets to announce the layoffs via Zoom. We were told 'market conditions' required 'difficult decisions'. The whole system is rigged.",
                author="capitalism_critic",
                created_utc=datetime.now().timestamp() - 864000,
                score=15678,
                upvote_ratio=0.92,
                num_comments=2341,
                url="https://reddit.com/r/antiwork/sample10",
                permalink="/r/antiwork/sample10",
                flair="Discussion",
                is_self=True,
            ),
            RedditPost(
                id="sample11",
                subreddit="construction",
                title="Construction slowdown - projects getting cancelled, workers being let go",
                selftext="The construction industry is feeling the pinch. Interest rates have killed new projects. Commercial real estate is dead. Residential is slowing. Our company just laid off 40% of the crew. Experienced foremen and project managers are getting let go. If you're in construction, start saving now.",
                author="hardhat_worker",
                created_utc=datetime.now().timestamp() - 950400,
                score=876,
                upvote_ratio=0.90,
                num_comments=189,
                url="https://reddit.com/r/construction/sample11",
                permalink="/r/construction/sample11",
                flair="Industry News",
                is_self=True,
            ),
            RedditPost(
                id="sample12",
                subreddit="law",
                title="BigLaw associate layoffs increasing - even 'safe' jobs aren't safe",
                selftext="Major law firms are quietly laying off associates. Kirkland just let go of 30, Davis Polk around 25. M&A has dried up, IPOs are down. Partners are hoarding work. As a third-year associate, I'm scared. $200k in law school debt and no job security. Should have done CS instead.",
                author="stressed_associate",
                created_utc=datetime.now().timestamp() - 1036800,
                score=1234,
                upvote_ratio=0.87,
                num_comments=267,
                url="https://reddit.com/r/law/sample12",
                permalink="/r/law/sample12",
                flair="Career",
                is_self=True,
            ),
            RedditPost(
                id="sample13",
                subreddit="sales",
                title="SaaS sales layoffs everywhere - quota carrying reps getting cut",
                selftext="The SaaS sales bloodbath continues. Salesforce, HubSpot, Zoom - all cutting sales teams. I was a top performer with 130% quota attainment and still got laid off. Companies are cutting costs by eliminating the people who bring in revenue. Makes no sense. The job market for sales is brutal right now.",
                author="quota_crusher",
                created_utc=datetime.now().timestamp() - 1123200,
                score=1567,
                upvote_ratio=0.91,
                num_comments=334,
                url="https://reddit.com/r/sales/sample13",
                permalink="/r/sales/sample13",
                flair="Layoffs",
                is_self=True,
            ),
            RedditPost(
                id="sample14",
                subreddit="humanresources",
                title="HR being eliminated by AI - Our entire team was let go",
                selftext="Ironic situation - our HR team of 15 was just laid off because the company is moving to AI-powered HR software. We spent months implementing the very systems that replaced us. Recruiting, benefits administration, employee relations - all being automated. Even HR isn't safe from automation.",
                author="hr_professional",
                created_utc=datetime.now().timestamp() - 1209600,
                score=2890,
                upvote_ratio=0.93,
                num_comments=456,
                url="https://reddit.com/r/humanresources/sample14",
                permalink="/r/humanresources/sample14",
                flair="Discussion",
                is_self=True,
            ),
            RedditPost(
                id="sample15",
                subreddit="energy",
                title="Oil and gas layoffs - transitioning to renewable energy means job losses",
                selftext="Working in oil and gas for 20 years. Our company just announced 2,000 layoffs as they 'transition to clean energy'. The renewable energy jobs don't pay the same and require different skills. At 50, I'm supposed to reinvent myself. The energy transition is necessary but devastating for workers.",
                author="oilfield_vet",
                created_utc=datetime.now().timestamp() - 1296000,
                score=978,
                upvote_ratio=0.85,
                num_comments=234,
                url="https://reddit.com/r/energy/sample15",
                permalink="/r/energy/sample15",
                flair="Industry",
                is_self=True,
            ),
            RedditPost(
                id="sample16",
                subreddit="journalism",
                title="Another news outlet shutters - 200 journalists laid off",
                selftext="Local news is dying. Our newspaper just closed after 150 years. 200 journalists out of work. This is the third news outlet in our region to shut down this year. Democracy dies in darkness, and the darkness is spreading. Going to try freelancing but the pay is terrible.",
                author="ink_stained",
                created_utc=datetime.now().timestamp() - 1382400,
                score=1456,
                upvote_ratio=0.94,
                num_comments=312,
                url="https://reddit.com/r/journalism/sample16",
                permalink="/r/journalism/sample16",
                flair="Job Market",
                is_self=True,
            ),
            RedditPost(
                id="sample17",
                subreddit="startups",
                title="Series B startup ran out of runway - entire company laid off",
                selftext="Startup life reality check. We raised $30M Series B two years ago. Burned through it chasing growth. VCs wouldn't fund the next round. Entire company of 85 people laid off with two weeks severance. Executives got golden parachutes. The startup dream is over for many of us.",
                author="startup_refugee",
                created_utc=datetime.now().timestamp() - 1468800,
                score=2234,
                upvote_ratio=0.90,
                num_comments=445,
                url="https://reddit.com/r/startups/sample17",
                permalink="/r/startups/sample17",
                flair="Failure",
                is_self=True,
            ),
            RedditPost(
                id="sample18",
                subreddit="pharmacy",
                title="Pharmacy layoffs - CVS and Walgreens cutting pharmacists and techs",
                selftext="Retail pharmacy is in crisis. CVS laid off hundreds of pharmacists. Walgreens closing 450 stores. Prescription volumes are down, reimbursements are down, workloads are up. I'm a pharmacist with $180k in debt and my job security is gone. Considering leaving the profession entirely.",
                author="rxfrustrated",
                created_utc=datetime.now().timestamp() - 1555200,
                score=1678,
                upvote_ratio=0.92,
                num_comments=378,
                url="https://reddit.com/r/pharmacy/sample18",
                permalink="/r/pharmacy/sample18",
                flair="Career",
                is_self=True,
            ),
            RedditPost(
                id="sample19",
                subreddit="gamedev",
                title="Gaming industry mass layoffs - Unity, EA, Epic all cutting staff",
                selftext="The gaming industry is hemorrhaging jobs. Unity laid off 1,800 people, EA cut 700, Epic let go 900. Even successful studios are cutting. Worked on AAA titles for 12 years, thought I was safe. Now I'm another unemployed game developer competing for scraps. The industry treats workers as disposable.",
                author="game_dev_down",
                created_utc=datetime.now().timestamp() - 1641600,
                score=3456,
                upvote_ratio=0.94,
                num_comments=567,
                url="https://reddit.com/r/gamedev/sample19",
                permalink="/r/gamedev/sample19",
                flair="Career",
                is_self=True,
            ),
            RedditPost(
                id="sample20",
                subreddit="consulting",
                title="McKinsey and BCG cutting consultants - even MBB isn't safe",
                selftext="The prestigious consulting firms are finally feeling the pain. McKinsey let go of 1,400, BCG around 800. Project pipelines are dry. Clients are cutting consulting budgets. As a post-MBA consultant, I thought I was set. Now updating my resume. The 'exit opps' everyone talked about are harder to find too.",
                author="consultant_concerned",
                created_utc=datetime.now().timestamp() - 1728000,
                score=2123,
                upvote_ratio=0.88,
                num_comments=423,
                url="https://reddit.com/r/consulting/sample20",
                permalink="/r/consulting/sample20",
                flair="MBB",
                is_self=True,
            ),
        ]

        if subreddit_name:
            return [p for p in sample_posts if p.subreddit.lower() == subreddit_name.lower()]
        return sample_posts

    def _get_sample_comments(self, post_id: str) -> List[RedditComment]:
        """Generate sample comments for testing"""
        sample_comments_map = {
            "sample1": [
                RedditComment(
                    id="c1_1",
                    post_id="sample1",
                    subreddit="layoffs",
                    body="Same thing happened to me last month. The tech industry has completely changed. Hang in there, it took me 3 months but I finally found something. Your distributed systems experience is valuable.",
                    author="fellow_googler",
                    created_utc=datetime.now().timestamp() - 80000,
                    score=456,
                    parent_id="sample1",
                    is_submitter=False,
                ),
                RedditComment(
                    id="c1_2",
                    post_id="sample1",
                    subreddit="layoffs",
                    body="The job market is terrible right now. I've been applying for 6 months with no luck. Companies are posting jobs but not actually hiring. It's demoralizing.",
                    author="job_seeker_sad",
                    created_utc=datetime.now().timestamp() - 75000,
                    score=234,
                    parent_id="sample1",
                    is_submitter=False,
                ),
                RedditComment(
                    id="c1_3",
                    post_id="sample1",
                    subreddit="layoffs",
                    body="I was laid off from Meta in November. It's been rough but I've used the time to upskill. Learning rust and systems programming. Stay positive!",
                    author="optimistic_dev",
                    created_utc=datetime.now().timestamp() - 70000,
                    score=189,
                    parent_id="sample1",
                    is_submitter=False,
                ),
            ],
            "sample2": [
                RedditComment(
                    id="c2_1",
                    post_id="sample2",
                    subreddit="cscareerquestions",
                    body="Start interviewing now. Don't wait until you get the notice. The market is competitive and the interview process takes months.",
                    author="pragmatic_engineer",
                    created_utc=datetime.now().timestamp() - 160000,
                    score=678,
                    parent_id="sample2",
                    is_submitter=False,
                ),
                RedditComment(
                    id="c2_2",
                    post_id="sample2",
                    subreddit="cscareerquestions",
                    body="I'm so tired of the anxiety. Every week there's news of more layoffs. Can't focus on my work because I'm constantly worried about being next.",
                    author="anxious_worker",
                    created_utc=datetime.now().timestamp() - 155000,
                    score=543,
                    parent_id="sample2",
                    is_submitter=False,
                ),
            ],
            "sample5": [
                RedditComment(
                    id="c5_1",
                    post_id="sample5",
                    subreddit="recruitinghell",
                    body="The ghost job phenomenon is real and it's destroying job seekers' mental health. Companies need to be held accountable for fake postings.",
                    author="fed_up_applicant",
                    created_utc=datetime.now().timestamp() - 400000,
                    score=1234,
                    parent_id="sample5",
                    is_submitter=False,
                ),
                RedditComment(
                    id="c5_2",
                    post_id="sample5",
                    subreddit="recruitinghell",
                    body="I've started networking more instead of just applying online. It's the only way to get your resume actually looked at by a human.",
                    author="networking_newbie",
                    created_utc=datetime.now().timestamp() - 395000,
                    score=567,
                    parent_id="sample5",
                    is_submitter=False,
                ),
                RedditComment(
                    id="c5_3",
                    post_id="sample5",
                    subreddit="recruitinghell",
                    body="500 applications and only 3 interviews is unfortunately normal now. The system is broken. ATS rejects qualified candidates constantly.",
                    author="recruiter_insider",
                    created_utc=datetime.now().timestamp() - 390000,
                    score=890,
                    parent_id="sample5",
                    is_submitter=False,
                ),
            ],
        }

        return sample_comments_map.get(post_id, [])


def main():
    """Main function to run the scraper"""
    # Use sample data by default (set to False if you have Reddit API credentials)
    scraper = RedditScraper(use_sample_data=True)

    # Scrape all target subreddits
    data = scraper.scrape_all(
        subreddits=TARGET_SUBREDDITS[:5],  # Limit for demo
        posts_per_subreddit=50,
        include_comments=True,
        time_filter="month"
    )

    # Save the data
    scraper.save_data(data)

    print(f"\nScraped {data['metadata']['total_posts']} posts and {data['metadata']['total_comments']} comments")
    print(f"Data saved to {DATA_DIR}/reddit_data.json")


if __name__ == "__main__":
    main()
