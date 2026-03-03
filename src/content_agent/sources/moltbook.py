"""
Moltbook API integration for content aggregation and publishing.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Any, Optional


class MoltbookAPI:
    """
    Official Moltbook API client.
    
    Supports:
    - Fetching posts
    - Creating posts
    - Replying to comments
    - Getting user stats
    """
    
    BASE_URL = "https://www.moltbook.com/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, 
                 data: Optional[Dict] = None) -> Dict:
        """Make authenticated API request."""
        url = f"{self.BASE_URL}{endpoint}"
        
        req = urllib.request.Request(
            url,
            headers=self.headers,
            method=method
        )
        
        if data:
            req.data = json.dumps(data).encode('utf-8')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"API Error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def get_posts(self, submolt: str = "general", 
                  limit: int = 20) -> List[Dict]:
        """
        Fetch recent posts from Moltbook.
        
        Args:
            submolt: Submolt/community name
            limit: Number of posts to fetch
            
        Returns:
            List of post dictionaries
        """
        response = self._request(
            "GET", 
            f"/posts?submolt={submolt}&limit={limit}"
        )
        
        posts = response.get("posts", [])
        
        # Normalize format
        return [
            {
                "id": post.get("id"),
                "title": post.get("title"),
                "content": post.get("content"),
                "author": post.get("author", {}).get("name"),
                "author_id": post.get("author", {}).get("id"),
                "upvotes": post.get("upvotes", 0),
                "comment_count": post.get("comment_count", 0),
                "created_at": post.get("created_at"),
                "platform": "moltbook"
            }
            for post in posts
        ]
    
    def create_post(self, title: str, content: str,
                    submolt: str = "general") -> Dict:
        """
        Create a new post on Moltbook.
        
        Args:
            title: Post title
            content: Post content (markdown supported)
            submolt: Target submolt
            
        Returns:
            Created post data
        """
        data = {
            "title": title,
            "content": content,
            "submolt": submolt
        }
        
        response = self._request("POST", "/posts", data)
        
        # Handle verification challenge
        if response.get("verification"):
            verification = response["verification"]
            print(f"Verification required: {verification['challenge_text']}")
            # TODO: Solve verification challenge
            # This would need LLM integration to solve math problems
            
        return response
    
    def get_comments(self, post_id: str) -> List[Dict]:
        """
        Get comments for a post.
        
        Args:
            post_id: Post ID
            
        Returns:
            List of comments
        """
        response = self._request("GET", f"/posts/{post_id}/comments")
        
        comments = response.get("comments", [])
        return [
            {
                "id": comment.get("id"),
                "content": comment.get("content"),
                "author": comment.get("author", {}).get("name"),
                "created_at": comment.get("created_at"),
                "platform": "moltbook"
            }
            for comment in comments
        ]
    
    def reply_to_comment(self, post_id: str, comment_id: str,
                         content: str) -> Dict:
        """
        Reply to a comment.
        
        Args:
            post_id: Parent post ID
            comment_id: Comment to reply to
            content: Reply content
            
        Returns:
            Created reply data
        """
        data = {
            "content": content,
            "parent_id": comment_id
        }
        
        return self._request(
            "POST", 
            f"/posts/{post_id}/comments", 
            data
        )
    
    def get_user_profile(self) -> Dict:
        """Get current user profile."""
        return self._request("GET", "/me")
    
    def get_user_posts(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get posts by a specific user."""
        response = self._request(
            "GET",
            f"/posts?author_id={user_id}&limit={limit}"
        )
        return response.get("posts", [])


class MoltbookSource:
    """Content source for Moltbook aggregation."""
    
    def __init__(self, api_key: str):
        self.api = MoltbookAPI(api_key)
    
    def fetch_posts(self, since: Optional[datetime] = None,
                    limit: int = 50) -> List[Dict]:
        """Fetch posts for content aggregation."""
        posts = self.api.get_posts(limit=limit)
        
        # Filter by date if specified
        if since:
            posts = [
                p for p in posts
                if datetime.fromisoformat(p["created_at"].replace('Z', '+00:00')) > since
            ]
        
        return posts


class MoltbookPublisher:
    """Content publisher for Moltbook."""
    
    def __init__(self, api_key: str):
        self.api = MoltbookAPI(api_key)
    
    def publish(self, post: Dict) -> Dict:
        """
        Publish content to Moltbook.
        
        Args:
            post: Dict with title, content, optional submolt
            
        Returns:
            Published post data
        """
        return self.api.create_post(
            title=post["title"],
            content=post["content"],
            submolt=post.get("submolt", "general")
        )
    
    def get_comments(self, post_id: str) -> List[Dict]:
        """Get comments for engagement."""
        return self.api.get_comments(post_id)
    
    def reply(self, comment_id: str, content: str,
              post_id: Optional[str] = None) -> Dict:
        """Reply to a comment."""
        # Note: Moltbook API needs post_id for replies
        if post_id is None:
            raise ValueError("post_id required for Moltbook replies")
        
        return self.api.reply_to_comment(post_id, comment_id, content)
