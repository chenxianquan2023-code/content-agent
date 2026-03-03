"""
ML-based optimal posting time prediction.
Predicts best times to post for maximum engagement.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class PostPerformance:
    """Performance metrics for a single post."""
    post_id: str
    platform: str
    posted_at: datetime
    hour: int
    day_of_week: int
    engagement_score: float
    likes: int
    comments: int
    shares: int


class OptimalTimePredictor:
    """
    Predicts optimal posting times using historical data.
    
    Features:
    - Hourly engagement patterns
    - Day of week analysis
    - Platform-specific optimization
    - Trend detection
    """
    
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.performance_history: List[PostPerformance] = []
        self._load_history()
    
    def _load_history(self):
        """Load historical performance data."""
        history = self.memory.cold("post_performance_history")
        if history:
            self.performance_history = [
                PostPerformance(
                    post_id=p["post_id"],
                    platform=p["platform"],
                    posted_at=datetime.fromisoformat(p["posted_at"]),
                    hour=p["hour"],
                    day_of_week=p["day_of_week"],
                    engagement_score=p["engagement_score"],
                    likes=p["likes"],
                    comments=p["comments"],
                    shares=p["shares"]
                )
                for p in history
            ]
    
    def record_performance(self, post_id: str, platform: str,
                          posted_at: datetime, metrics: Dict):
        """
        Record performance for a post.
        
        Args:
            post_id: Post identifier
            platform: Platform name
            posted_at: When post was published
            metrics: Dict with likes, comments, shares, etc.
        """
        # Calculate engagement score
        engagement = self._calculate_engagement(metrics)
        
        performance = PostPerformance(
            post_id=post_id,
            platform=platform,
            posted_at=posted_at,
            hour=posted_at.hour,
            day_of_week=posted_at.weekday(),
            engagement_score=engagement,
            likes=metrics.get("likes", 0),
            comments=metrics.get("comments", 0),
            shares=metrics.get("shares", 0)
        )
        
        self.performance_history.append(performance)
        
        # Keep only last 1000 records
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
        
        self._save_history()
    
    def _calculate_engagement(self, metrics: Dict) -> float:
        """Calculate weighted engagement score."""
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)
        shares = metrics.get("shares", 0)
        views = metrics.get("views", 1)
        
        # Weighted score: shares > comments > likes
        score = (likes * 1 + comments * 3 + shares * 5) / max(views, 1)
        return score
    
    def predict_best_times(self, platform: str, 
                          days_ahead: int = 7) -> List[Dict]:
        """
        Predict best posting times for upcoming days.
        
        Args:
            platform: Target platform
            days_ahead: How many days to predict
            
        Returns:
            List of recommended times with confidence scores
        """
        # Filter history for this platform
        platform_history = [
            p for p in self.performance_history
            if p.platform == platform
        ]
        
        if len(platform_history) < 5:
            # Not enough data, return defaults
            return self._get_default_times(days_ahead)
        
        # Analyze hourly patterns
        hourly_scores = {h: [] for h in range(24)}
        for p in platform_history:
            hourly_scores[p.hour].append(p.engagement_score)
        
        # Calculate average engagement per hour
        hourly_avg = {}
        for hour, scores in hourly_scores.items():
            if scores:
                hourly_avg[hour] = statistics.mean(scores)
            else:
                hourly_avg[hour] = 0
        
        # Analyze day of week patterns
        daily_scores = {d: [] for d in range(7)}
        for p in platform_history:
            daily_scores[p.day_of_week].append(p.engagement_score)
        
        daily_avg = {}
        for day, scores in daily_scores.items():
            if scores:
                daily_avg[day] = statistics.mean(scores)
            else:
                daily_avg[day] = 0
        
        # Predict for upcoming days
        recommendations = []
        now = datetime.now()
        
        for day_offset in range(days_ahead):
            target_date = now + timedelta(days=day_offset)
            target_day = target_date.weekday()
            
            # Find best hours for this day
            day_scores = []
            for hour in range(24):
                # Combined score: hour performance + day performance
                hour_score = hourly_avg.get(hour, 0)
                day_score = daily_avg.get(target_day, 0)
                combined = hour_score * 0.7 + day_score * 0.3
                
                day_scores.append({
                    "hour": hour,
                    "score": combined,
                    "confidence": min(len(platform_history) / 50, 1.0)
                })
            
            # Sort by score
            day_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Top 3 times for this day
            for slot in day_scores[:3]:
                recommendations.append({
                    "datetime": target_date.replace(hour=slot["hour"], minute=0),
                    "hour": slot["hour"],
                    "day": target_date.strftime("%A"),
                    "predicted_engagement": round(slot["score"], 3),
                    "confidence": round(slot["confidence"], 2),
                    "platform": platform
                })
        
        # Sort all by predicted engagement
        recommendations.sort(key=lambda x: x["predicted_engagement"], reverse=True)
        
        return recommendations[:10]  # Top 10 overall
    
    def get_hourly_heatmap(self, platform: str) -> List[List[float]]:
        """
        Get engagement heatmap by hour and day.
        
        Returns:
            7x24 matrix (days x hours) with engagement scores
        """
        platform_history = [
            p for p in self.performance_history
            if p.platform == platform
        ]
        
        # Initialize 7x24 matrix
        heatmap = [[0.0 for _ in range(24)] for _ in range(7)]
        counts = [[0 for _ in range(24)] for _ in range(7)]
        
        # Aggregate data
        for p in platform_history:
            heatmap[p.day_of_week][p.hour] += p.engagement_score
            counts[p.day_of_week][p.hour] += 1
        
        # Normalize
        for day in range(7):
            for hour in range(24):
                if counts[day][hour] > 0:
                    heatmap[day][hour] /= counts[day][hour]
        
        return heatmap
    
    def get_insights(self, platform: str) -> Dict:
        """Get actionable insights about posting times."""
        platform_history = [
            p for p in self.performance_history
            if p.platform == platform
        ]
        
        if not platform_history:
            return {"error": "Not enough data"}
        
        # Find best and worst times
        hourly_avg = {}
        for hour in range(24):
            scores = [p.engagement_score for p in platform_history if p.hour == hour]
            if scores:
                hourly_avg[hour] = statistics.mean(scores)
        
        best_hour = max(hourly_avg.items(), key=lambda x: x[1])
        worst_hour = min(hourly_avg.items(), key=lambda x: x[1])
        
        # Day of week analysis
        daily_avg = {}
        for day in range(7):
            scores = [p.engagement_score for p in platform_history if p.day_of_week == day]
            if scores:
                daily_avg[day] = statistics.mean(scores)
        
        best_day = max(daily_avg.items(), key=lambda x: x[1]) if daily_avg else (0, 0)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "best_time": f"{best_hour[0]:02d}:00 ({best_hour[1]:.2f} avg engagement)",
            "worst_time": f"{worst_hour[0]:02d}:00 ({worst_hour[1]:.2f} avg engagement)",
            "best_day": f"{days[best_day[0]]} ({best_day[1]:.2f} avg engagement)",
            "data_points": len(platform_history),
            "avg_engagement": statistics.mean([p.engagement_score for p in platform_history]),
            "improvement_potential": round(best_hour[1] / max(worst_hour[1], 0.01), 2)
        }
    
    def _get_default_times(self, days_ahead: int) -> List[Dict]:
        """Return default posting times when no data available."""
        defaults = []
        now = datetime.now()
        
        # Default good times: 9am, 2pm, 8pm
        default_hours = [9, 14, 20]
        
        for day_offset in range(days_ahead):
            target_date = now + timedelta(days=day_offset)
            for hour in default_hours:
                defaults.append({
                    "datetime": target_date.replace(hour=hour, minute=0),
                    "hour": hour,
                    "day": target_date.strftime("%A"),
                    "predicted_engagement": 0.5,
                    "confidence": 0.0,
                    "note": "Default (insufficient data)"
                })
        
        return defaults
    
    def _save_history(self):
        """Save performance history to memory."""
        data = [
            {
                "post_id": p.post_id,
                "platform": p.platform,
                "posted_at": p.posted_at.isoformat(),
                "hour": p.hour,
                "day_of_week": p.day_of_week,
                "engagement_score": p.engagement_score,
                "likes": p.likes,
                "comments": p.comments,
                "shares": p.shares
            }
            for p in self.performance_history
        ]
        
        self.memory.cold("post_performance_history", data)
