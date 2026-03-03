"""
Discord integration via Webhook and Bot API.
"""

import json
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional


class DiscordWebhook:
    """
    Discord Webhook client for posting messages.
    
    Simple way to post to Discord without bot setup.
    """
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, content: str = None, embeds: List[Dict] = None,
             username: str = None, avatar_url: str = None) -> Dict:
        """
        Send message to Discord channel.
        
        Args:
            content: Plain text message
            embeds: Rich embeds (up to 10)
            username: Override webhook username
            avatar_url: Override webhook avatar
            
        Returns:
            Response data
        """
        data = {}
        
        if content:
            data["content"] = content
        
        if embeds:
            data["embeds"] = embeds
        
        if username:
            data["username"] = username
        
        if avatar_url:
            data["avatar_url"] = avatar_url
        
        headers = {
            "Content-Type": "application/json"
        }
        
        req = urllib.request.Request(
            self.webhook_url,
            data=json.dumps(data).encode(),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return {"status": "sent", "code": response.getcode()}
        except Exception as e:
            raise Exception(f"Discord webhook error: {e}")
    
    def send_rich(self, title: str, description: str,
                  fields: List[Dict] = None, color: int = 0x00ff00,
                  url: str = None, image: str = None) -> Dict:
        """
        Send rich embed message.
        
        Args:
            title: Embed title
            description: Embed description
            fields: List of field dicts with name/value/inline
            color: Sidebar color (hex int)
            url: URL for title
            image: Image URL
        """
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if url:
            embed["url"] = url
        
        if fields:
            embed["fields"] = fields
        
        if image:
            embed["image"] = {"url": image}
        
        return self.send(embeds=[embed])


class DiscordBotAPI:
    """
    Discord Bot API client (requires bot token).
    
    More powerful than webhooks - can read messages,
    manage channels, etc.
    """
    
    BASE_URL = "https://discord.com/api/v10"
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make API request."""
        url = f"{self.BASE_URL}{endpoint}"
        
        req = urllib.request.Request(
            url,
            headers=self.headers,
            method=method
        )
        
        if data:
            req.data = json.dumps(data).encode()
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            raise Exception(f"Discord API error: {e}")
    
    def get_channel_messages(self, channel_id: str, 
                            limit: int = 50) -> List[Dict]:
        """Get recent messages from a channel."""
        endpoint = f"/channels/{channel_id}/messages?limit={limit}"
        
        messages = self._request("GET", endpoint)
        
        return [
            {
                "id": msg.get("id"),
                "content": msg.get("content"),
                "author": msg.get("author", {}).get("username"),
                "author_id": msg.get("author", {}).get("id"),
                "timestamp": msg.get("timestamp"),
                "reactions": len(msg.get("reactions", [])),
                "platform": "discord"
            }
            for msg in messages
        ]
    
    def send_message(self, channel_id: str, content: str,
                     embeds: List[Dict] = None) -> Dict:
        """Send message to channel."""
        endpoint = f"/channels/{channel_id}/messages"
        
        data = {"content": content}
        if embeds:
            data["embeds"] = embeds
        
        return self._request("POST", endpoint, data)
    
    def reply_to_message(self, channel_id: str, message_id: str,
                        content: str) -> Dict:
        """Reply to a specific message."""
        endpoint = f"/channels/{channel_id}/messages"
        
        data = {
            "content": content,
            "message_reference": {
                "message_id": message_id
            }
        }
        
        return self._request("POST", endpoint, data)


class DiscordSource:
    """Discord content source (requires bot)."""
    
    def __init__(self, bot_token: str, channel_id: str):
        self.api = DiscordBotAPI(bot_token)
        self.channel_id = channel_id
    
    def fetch_posts(self, since: Optional[datetime] = None,
                    limit: int = 50) -> List[Dict]:
        """Fetch messages from Discord channel."""
        messages = self.api.get_channel_messages(self.channel_id, limit)
        
        # Filter by date
        if since:
            messages = [
                m for m in messages
                if datetime.fromisoformat(m["timestamp"].replace('Z', '+00:00')) > since
            ]
        
        return messages


class DiscordPublisher:
    """Discord content publisher via webhook."""
    
    def __init__(self, webhook_url: str):
        self.webhook = DiscordWebhook(webhook_url)
    
    def publish(self, post: Dict) -> Dict:
        """Publish to Discord as rich embed."""
        title = post.get("title", "New Content")
        content = post.get("content", "")
        
        # Split long content
        if len(content) > 4000:
            content = content[:3997] + "..."
        
        return self.webhook.send_rich(
            title=title,
            description=content,
            color=0x5865f2  # Discord blurple
        )
    
    def reply(self, message_id: str, content: str) -> Dict:
        """Note: Webhooks can't reply to specific messages."""
        # Just send a new message mentioning context
        return self.webhook.send(f"> Replying to message\n{content}")
