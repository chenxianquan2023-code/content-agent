"""
虾聊 (ClawdChat) API integration.
"""

import json
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional


class ClawdchatAPI:
    """
    虾聊 API 客户端。
    
    支持：
    - 获取帖子
    - 创建帖子
    - 回复评论
    - 获取用户信息
    """
    
    BASE_URL = "https://clawdchat.cn/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str,
                 data: Optional[Dict] = None) -> Dict:
        """发起认证 API 请求。"""
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
        except Exception as e:
            raise Exception(f"请求失败: {e}")
    
    def get_posts(self, circle: str = "ai-doers",
                  limit: int = 20) -> List[Dict]:
        """
        获取虾聊帖子。
        
        Returns:
            帖子列表
        """
        response = self._request(
            "GET",
            f"/posts?circle={circle}&limit={limit}"
        )
        
        posts = response.get("posts", [])
        
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
                "platform": "clawdchat"
            }
            for post in posts
        ]
    
    def create_post(self, title: str, content: str,
                    circle: str = "ai-doers") -> Dict:
        """创建新帖子。"""
        data = {
            "title": title,
            "content": content,
            "circle": circle
        }
        
        return self._request("POST", "/posts", data)
    
    def get_comments(self, post_id: str) -> List[Dict]:
        """获取评论。"""
        response = self._request("GET", f"/posts/{post_id}/comments")
        
        comments = response.get("comments", [])
        return [
            {
                "id": c.get("id"),
                "content": c.get("content"),
                "author": c.get("author", {}).get("name"),
                "created_at": c.get("created_at"),
                "platform": "clawdchat"
            }
            for c in comments
        ]
    
    def reply_to_comment(self, post_id: str, content: str) -> Dict:
        """回复帖子（虾聊直接回复帖子）。"""
        data = {"content": content}
        return self._request("POST", f"/posts/{post_id}/comments", data)


class ClawdchatSource:
    """虾聊内容源。"""
    
    def __init__(self, api_key: str):
        self.api = ClawdchatAPI(api_key)
    
    def fetch_posts(self, since: Optional[datetime] = None,
                    limit: int = 50) -> List[Dict]:
        """获取帖子用于内容聚合。"""
        posts = self.api.get_posts(limit=limit)
        
        if since:
            posts = [
                p for p in posts
                if datetime.fromisoformat(p["created_at"].replace('Z', '+00:00')) > since
            ]
        
        return posts


class ClawdchatPublisher:
    """虾聊内容发布器。"""
    
    def __init__(self, api_key: str):
        self.api = ClawdchatAPI(api_key)
    
    def publish(self, post: Dict) -> Dict:
        """发布内容到虾聊。"""
        return self.api.create_post(
            title=post["title"],
            content=post["content"],
            circle=post.get("circle", "ai-doers")
        )
    
    def get_comments(self, post_id: str) -> List[Dict]:
        return self.api.get_comments(post_id)
    
    def reply(self, comment_id: str, content: str,
              post_id: Optional[str] = None) -> Dict:
        """回复评论。"""
        if post_id is None:
            raise ValueError("post_id 是必需的")
        return self.api.reply_to_comment(post_id, content)
