"""
Content performance analytics and reporting.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics


class ContentAnalytics:
    """
    Analyze content performance and provide insights.
    
    Features:
    - Engagement tracking
    - Content type analysis
    - Trend detection
    - Competitor benchmarking
    - Automated reports
    """
    
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.reports_dir = self.memory.workspace / "analytics"
        self.reports_dir.mkdir(exist_ok=True)
    
    def track_post(self, post_id: str, platform: str,
                   content_type: str, metadata: Dict):
        """
        Track a post for analytics.
        
        Args:
            post_id: Post identifier
            platform: Platform name
            content_type: Type of content (news, insight, summary, etc.)
            metadata: Content metadata (topics, length, etc.)
        """
        tracking_data = {
            "post_id": post_id,
            "platform": platform,
            "content_type": content_type,
            "posted_at": datetime.now().isoformat(),
            "metadata": metadata,
            "engagement": {
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "views": 0
            },
            "updated_at": datetime.now().isoformat()
        }
        
        # Store in memory
        key = f"tracking_{platform}_{post_id}"
        self.memory.warm(key, tracking_data)
    
    def update_engagement(self, post_id: str, platform: str,
                         metrics: Dict):
        """
        Update engagement metrics for a tracked post.
        
        Args:
            post_id: Post identifier
            platform: Platform name
            metrics: Dict with likes, comments, shares, views
        """
        key = f"tracking_{platform}_{post_id}"
        tracking = self.memory.warm(key)
        
        if tracking:
            tracking["engagement"].update(metrics)
            tracking["updated_at"] = datetime.now().isoformat()
            self.memory.warm(key, tracking)
    
    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Report dict with metrics and insights
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Collect all tracked posts
        all_posts = []
        for key in self.memory.warm_dir.glob("tracking_*.json"):
            data = self.memory.warm(key.stem)
            if data:
                posted_at = datetime.fromisoformat(data["posted_at"])
                if posted_at > cutoff:
                    all_posts.append(data)
        
        if not all_posts:
            return {"error": "No data available for report period"}
        
        # Calculate metrics
        report = {
            "period": f"Last {days} days",
            "generated_at": datetime.now().isoformat(),
            "summary": self._calculate_summary(all_posts),
            "by_platform": self._analyze_by_platform(all_posts),
            "by_content_type": self._analyze_by_type(all_posts),
            "top_performing": self._get_top_posts(all_posts, 5),
            "trends": self._detect_trends(all_posts),
            "recommendations": self._generate_recommendations(all_posts)
        }
        
        # Save report
        report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.memory.cold(f"analytics_report_{report_id}", report)
        
        return report
    
    def _calculate_summary(self, posts: List[Dict]) -> Dict:
        """Calculate overall summary metrics."""
        total_posts = len(posts)
        
        total_likes = sum(p["engagement"]["likes"] for p in posts)
        total_comments = sum(p["engagement"]["comments"] for p in posts)
        total_shares = sum(p["engagement"]["shares"] for p in posts)
        total_views = sum(p["engagement"]["views"] for p in posts)
        
        # Calculate engagement rate
        engagement_rates = []
        for p in posts:
            views = max(p["engagement"]["views"], 1)
            engagement = (p["engagement"]["likes"] + 
                         p["engagement"]["comments"] * 2 + 
                         p["engagement"]["shares"] * 3)
            engagement_rates.append(engagement / views)
        
        avg_engagement_rate = statistics.mean(engagement_rates) if engagement_rates else 0
        
        return {
            "total_posts": total_posts,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_views": total_views,
            "avg_engagement_rate": round(avg_engagement_rate * 100, 2),
            "avg_likes_per_post": round(total_likes / max(total_posts, 1), 1),
            "avg_comments_per_post": round(total_comments / max(total_posts, 1), 1)
        }
    
    def _analyze_by_platform(self, posts: List[Dict]) -> Dict:
        """Analyze performance by platform."""
        by_platform = defaultdict(lambda: {
            "posts": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "views": 0
        })
        
        for post in posts:
            platform = post["platform"]
            by_platform[platform]["posts"] += 1
            by_platform[platform]["likes"] += post["engagement"]["likes"]
            by_platform[platform]["comments"] += post["engagement"]["comments"]
            by_platform[platform]["shares"] += post["engagement"]["shares"]
            by_platform[platform]["views"] += post["engagement"]["views"]
        
        # Calculate averages
        result = {}
        for platform, data in by_platform.items():
            posts_count = data["posts"]
            result[platform] = {
                "posts": posts_count,
                "avg_likes": round(data["likes"] / posts_count, 1),
                "avg_comments": round(data["comments"] / posts_count, 1),
                "avg_shares": round(data["shares"] / posts_count, 1),
                "total_views": data["views"],
                "engagement_score": round(
                    (data["likes"] + data["comments"] * 2 + data["shares"] * 3) / max(data["views"], 1),
                    3
                )
            }
        
        return result
    
    def _analyze_by_type(self, posts: List[Dict]) -> Dict:
        """Analyze performance by content type."""
        by_type = defaultdict(lambda: {
            "posts": 0,
            "total_engagement": 0
        })
        
        for post in posts:
            content_type = post.get("content_type", "unknown")
            engagement = (post["engagement"]["likes"] + 
                         post["engagement"]["comments"] * 2 +
                         post["engagement"]["shares"] * 3)
            
            by_type[content_type]["posts"] += 1
            by_type[content_type]["total_engagement"] += engagement
        
        # Sort by performance
        result = {}
        for content_type, data in sorted(by_type.items(), 
                                         key=lambda x: x[1]["total_engagement"],
                                         reverse=True):
            result[content_type] = {
                "posts": data["posts"],
                "total_engagement": data["total_engagement"],
                "avg_engagement": round(data["total_engagement"] / data["posts"], 1)
            }
        
        return result
    
    def _get_top_posts(self, posts: List[Dict], n: int = 5) -> List[Dict]:
        """Get top performing posts."""
        # Calculate engagement score for each post
        scored_posts = []
        for post in posts:
            score = (post["engagement"]["likes"] + 
                    post["engagement"]["comments"] * 2 +
                    post["engagement"]["shares"] * 3)
            
            scored_posts.append({
                "post_id": post["post_id"],
                "platform": post["platform"],
                "content_type": post.get("content_type"),
                "engagement_score": score,
                "likes": post["engagement"]["likes"],
                "comments": post["engagement"]["comments"],
                "shares": post["engagement"]["shares"],
                "posted_at": post["posted_at"]
            })
        
        # Sort by score
        scored_posts.sort(key=lambda x: x["engagement_score"], reverse=True)
        
        return scored_posts[:n]
    
    def _detect_trends(self, posts: List[Dict]) -> Dict:
        """Detect trends in the data."""
        trends = {
            "engagement_trend": "stable",
            "volume_trend": "stable",
            "best_performing_topic": None
        }
        
        if len(posts) < 10:
            return trends
        
        # Sort by date
        sorted_posts = sorted(posts, key=lambda x: x["posted_at"])
        
        # Split into first and second half
        mid = len(sorted_posts) // 2
        first_half = sorted_posts[:mid]
        second_half = sorted_posts[mid:]
        
        # Calculate engagement for each half
        def avg_engagement(post_list):
            if not post_list:
                return 0
            total = sum(p["engagement"]["likes"] + p["engagement"]["comments"] 
                       for p in post_list)
            return total / len(post_list)
        
        first_eng = avg_engagement(first_half)
        second_eng = avg_engagement(second_half)
        
        # Determine trend
        if second_eng > first_eng * 1.2:
            trends["engagement_trend"] = "up"
        elif second_eng < first_eng * 0.8:
            trends["engagement_trend"] = "down"
        
        # Volume trend
        first_volume = len(first_half)
        second_volume = len(second_half)
        
        if second_volume > first_volume * 1.5:
            trends["volume_trend"] = "up"
        elif second_volume < first_volume * 0.5:
            trends["volume_trend"] = "down"
        
        return trends
    
    def _generate_recommendations(self, posts: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Analyze by type
        by_type = self._analyze_by_type(posts)
        
        if by_type:
            best_type = list(by_type.keys())[0]
            worst_type = list(by_type.keys())[-1]
            
            best_avg = by_type[best_type]["avg_engagement"]
            worst_avg = by_type[worst_type]["avg_engagement"]
            
            if best_avg > worst_avg * 1.5:
                recommendations.append(
                    f"Focus on '{best_type}' content - it performs "
                    f"{best_avg/worst_avg:.1f}x better than '{worst_type}'"
                )
        
        # Analyze by platform
        by_platform = self._analyze_by_platform(posts)
        
        if len(by_platform) > 1:
            best_platform = max(by_platform.items(), 
                              key=lambda x: x[1]["engagement_score"])
            recommendations.append(
                f"Prioritize {best_platform[0]} - highest engagement score "
                f"({best_platform[1]['engagement_score']:.3f})"
            )
        
        # General recommendations
        total_posts = len(posts)
        if total_posts < 7:
            recommendations.append(
                "Increase posting frequency to gather more data"
            )
        
        avg_likes = sum(p["engagement"]["likes"] for p in posts) / max(total_posts, 1)
        if avg_likes < 10:
            recommendations.append(
                "Consider adjusting content strategy - engagement is below target"
            )
        
        return recommendations
    
    def export_report_html(self, report: Dict, output_path: str):
        """Export report as HTML."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Content Analytics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }}
        h1 {{ color: #333; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
        .stat-box {{ background: #f0f0f0; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #4a90e2; }}
        .stat-label {{ color: #666; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4a90e2; color: white; }}
        .recommendations {{ background: #e8f4f8; padding: 20px; border-radius: 8px; margin-top: 30px; }}
        .recommendations li {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Content Analytics Report</h1>
        <p><strong>Period:</strong> {report['period']}</p>
        <p><strong>Generated:</strong> {report['generated_at']}</p>
        
        <div class="summary">
            <div class="stat-box">
                <div class="stat-value">{report['summary']['total_posts']}</div>
                <div class="stat-label">Total Posts</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{report['summary']['total_likes']}</div>
                <div class="stat-label">Total Likes</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{report['summary']['total_comments']}</div>
                <div class="stat-label">Comments</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{report['summary']['avg_engagement_rate']}%</div>
                <div class="stat-label">Avg Engagement</div>
            </div>
        </div>
        
        <div class="recommendations">
            <h2>💡 Recommendations</h2>
            <ul>
                {''.join(f'<li>{r}</li>' for r in report['recommendations'])}
            </ul>
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html)
