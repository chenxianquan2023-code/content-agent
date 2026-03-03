"""
Twitter/X API integration for content aggregation and publishing.
"""

import json
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional
import base64


class TwitterAPI:
    """
    Twitter/X API v2 client.
    
    Supports:
    - Fetching tweets from timeline
    - Searching tweets
    - Posting tweets
    - Replying to tweets
    """
    
    BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self, bearer_token: str, api_key: str = None, 
                 api_secret: str = None, access_token: str = None,
                 access_secret: str = None):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str,
                 data: Dict = None, use_user_auth: bool = False) -> Dict:
        """Make API request."""
        url = f"{self.BASE_URL}{endpoint}"
        
        headers = self.headers.copy()
        
        # For write operations, use OAuth 1.0a user context
        if use_user_auth and self.access_token:
            # In production, implement proper OAuth 1.0a signing
            # For now, this is a placeholder
            pass
        
        req = urllib.request.Request(
            url,
            headers=headers,
            method=method
        )
        
        if data:
            req.data = json.dumps(data).encode('utf-8')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise Exception(f"Twitter API error: {e}")
    
    def search_tweets(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search recent tweets.
        
        Args:
            query: Search query (supports Twitter search operators)
            max_results: Number of results (10-100)
            
        Returns:
            List of tweet dictionaries
        """
        encoded_query = urllib.parse.quote(query)
        endpoint = f"/tweets/search/recent?query={encoded_query}&max_results={max_results}&tweet.fields=created_at,author_id,public_metrics"
        
        response = self._request("GET", endpoint)
        
        tweets = response.get("data", [])
        return [
            {
                "id": tweet.get("id"),
                "text": tweet.get("text"),
                "author_id": tweet.get("author_id"),
                "created_at": tweet.get("created_at"),
                "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0),
                "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                "replies": tweet.get("public_metrics", {}).get("reply_count", 0),
                "platform": "twitter"
            }
            for tweet in tweets
        ]
    
    def get_user_timeline(self, user_id: str, max_results: int = 20) -> List[Dict]:
        """Get tweets from a user's timeline."""
        endpoint = f"/users/{user_id}/tweets?max_results={max_results}&tweet.fields=created_at,public_metrics"
        
        response = self._request("GET", endpoint)
        
        tweets = response.get("data", [])
        return [
            {
                "id": tweet.get("id"),
                "text": tweet.get("text"),
                "created_at": tweet.get("created_at"),
                "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0),
                "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                "platform": "twitter"
            }
            for tweet in tweets
        ]
    
    def post_tweet(self, text: str, reply_to: str = None) -> Dict:
        """
        Post a new tweet.
        
        Args:
            text: Tweet text (max 280 chars)
            reply_to: Tweet ID to reply to
            
        Returns:
            Created tweet data
        """
        data = {"text": text}
        
        if reply_to:
            data["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        return self._request("POST", "/tweets", data, use_user_auth=True)
    
    def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """Get engagement metrics for a tweet."""
        endpoint = f"/tweets/{tweet_id}?tweet.fields=public_metrics"
        
        response = self._request("GET", endpoint)
        tweet = response.get("data", {})
        metrics = tweet.get("public_metrics", {})
        
        return {
            "impressions": metrics.get("impression_count", 0),
            "engagements": metrics.get("engagement_count", 0),
            "retweets": metrics.get("retweet_count", 0),
            "replies": metrics.get("reply_count", 0),
            "likes": metrics.get("like_count", 0),
            "quotes": metrics.get("quote_count", 0)
        }


class TwitterSource:
    """Twitter content source."""
    
    def __init__(self, bearer_token: str):
        self.api = TwitterAPI(bearer_token)
    
    def fetch_posts(self, since: Optional[datetime] = None,
                    limit: int = 50) -> List[Dict]:
        """Fetch tweets for content aggregation."""
        # Search for AI-related tweets
        tweets = self.api.search_tweets(
            query="AI agent OR LLM OR OpenAI -is:retweet",
            max_results=min(limit, 100)
        )
        
        # Filter by date if specified
        if since:
            tweets = [
                t for t in tweets
                if datetime.fromisoformat(t["created_at"].replace('Z', '+00:00')) > since
            ]
        
        return tweets


class TwitterPublisher:
    """Twitter content publisher."""
    
    def __init__(self, bearer_token: str, api_key: str,
                 api_secret: str, access_token: str, access_secret: str):
        self.api = TwitterAPI(
            bearer_token, api_key, api_secret,
            access_token, access_secret
        )
    
    def publish(self, post: Dict) -> Dict:
        """
        Publish to Twitter.
        
        Note: Twitter has 280 char limit (or 4000 for Twitter Blue)
        """
        content = post.get("content", "")
        
        # Truncate if needed
        if len(content) > 280:
            content = content[:277] + "..."
        
        return self.api.post_tweet(content)
    
    def reply(self, tweet_id: str, content: str) -> Dict:
        """Reply to a tweet."""
        if len(content) > 280:
            content = content[:277] + "..."
        
        return self.api.post_tweet(content, reply_to=tweet_id)
