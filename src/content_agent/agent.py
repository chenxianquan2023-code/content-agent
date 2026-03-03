"""
Core Content Agent implementation.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import from agent-memory-kit
try:
    from agent_memory_kit import MemoryManager
except ImportError:
    # Try to find it in sibling directory (dev mode)
    import sys
    # content-agent/src/content_agent/agent.py -> content-agent/src -> content-agent -> projects -> agent-memory-kit/src
    amk_path = Path(__file__).parent.parent.parent.parent / "agent-memory-kit" / "src"
    if amk_path.exists():
        sys.path.insert(0, str(amk_path))
        from agent_memory_kit import MemoryManager
    else:
        raise ImportError(
            "agent_memory_kit not found. Install it with: pip install agent-memory-kit"
        )

from .strategy import ContentStrategy


class ContentAgent:
    """
    AI-powered content curation and publishing agent.
    
    Daily workflow:
    1. Aggregate content from sources
    2. Generate insights/summaries
    3. Create platform-specific posts
    4. Publish and monitor engagement
    """
    
    def __init__(self, 
                 workspace: str = "./content_agent",
                 strategy: Optional[ContentStrategy] = None,
                 sources: Optional[List[str]] = None,
                 platforms: Optional[List[str]] = None):
        
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Initialize memory system
        self.memory = MemoryManager(workspace)
        
        # Content strategy
        self.strategy = strategy or ContentStrategy()
        
        # Sources and platforms
        self.sources = sources or ["moltbook", "clawdchat"]
        self.platforms = platforms or ["moltbook", "clawdchat"]
        
        # Initialize components
        self._init_sources()
        self._init_publishers()
    
    def _init_sources(self):
        """Initialize content sources."""
        self.source_clients = {}
        
        # TODO: Implement source modules
        # For now, sources are not implemented yet
        pass
    
    def _init_publishers(self):
        """Initialize platform publishers."""
        self.publishers = {}
        
        # TODO: Implement publisher modules
        # For now, publishers are not implemented yet
        pass
    
    def daily_routine(self) -> Dict[str, Any]:
        """
        Execute the daily content routine.
        
        Returns:
            Report of what was done
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "aggregated": [],
            "generated": [],
            "published": [],
            "engaged": []
        }
        
        # Step 1: Aggregate content
        print("📥 Aggregating content...")
        raw_content = self._aggregate_content()
        report["aggregated"] = list(raw_content.keys())
        
        # Step 2: Generate insights
        print("🧠 Generating insights...")
        insights = self._generate_insights(raw_content)
        report["generated"] = [i["title"] for i in insights]
        
        # Step 3: Create and publish posts
        print("📝 Publishing content...")
        for insight in insights:
            for platform_name, publisher in self.publishers.items():
                try:
                    post = self._create_post(insight, platform_name)
                    result = publisher.publish(post)
                    report["published"].append({
                        "platform": platform_name,
                        "title": post["title"],
                        "status": "success"
                    })
                except Exception as e:
                    report["published"].append({
                        "platform": platform_name,
                        "title": insight["title"],
                        "status": "failed",
                        "error": str(e)
                    })
        
        # Step 4: Check yesterday's engagement
        print("💬 Checking engagement...")
        engagement = self._check_engagement()
        report["engaged"] = engagement
        
        # Save report to memory
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.memory.cold(f"daily_report_{date_str}", report)
        
        # Update last run time
        self.memory.warm("last_daily_run", datetime.now().isoformat())
        
        print(f"✅ Daily routine complete!")
        print(f"   Aggregated: {len(report['aggregated'])} sources")
        print(f"   Generated: {len(report['generated'])} insights")
        print(f"   Published: {len([p for p in report['published'] if p['status'] == 'success'])} posts")
        
        return report
    
    def _aggregate_content(self) -> Dict[str, List[Dict]]:
        """Aggregate content from all sources."""
        content = {}
        
        # Get last check time from memory
        last_check = self.memory.warm("last_content_check")
        if last_check:
            last_check = datetime.fromisoformat(last_check)
        else:
            last_check = datetime.now() - timedelta(days=1)
        
        # Fetch from each source
        for source_name, client in self.source_clients.items():
            try:
                posts = client.fetch_posts(since=last_check)
                content[source_name] = posts
                print(f"   ✓ {source_name}: {len(posts)} posts")
            except Exception as e:
                print(f"   ✗ {source_name}: {e}")
                content[source_name] = []
        
        # Update check time
        self.memory.warm("last_content_check", datetime.now().isoformat())
        
        # Store in HOT memory for processing
        self.memory.hot("today_content", content)
        
        return content
    
    def _generate_insights(self, content: Dict[str, List[Dict]]) -> List[Dict]:
        """Generate insights from aggregated content."""
        insights = []
        
        # Simple insight: trending topics
        all_titles = []
        for source_posts in content.values():
            for post in source_posts:
                all_titles.append(post.get("title", ""))
        
        # Generate a summary insight
        if all_titles:
            insight = {
                "title": f"AI Daily Digest - {datetime.now().strftime('%m/%d')}",
                "content": self._summarize_posts(all_titles[:10]),
                "sources": list(content.keys()),
                "generated_at": datetime.now().isoformat()
            }
            insights.append(insight)
        
        # Store insights
        self.memory.hot("today_insights", insights)
        
        return insights
    
    def _summarize_posts(self, titles: List[str]) -> str:
        """Generate summary from post titles."""
        # Simple summarization - in production, use LLM
        summary_parts = [
            "今日AI社区热点：",
            "",
            "【社区动态】",
        ]
        
        for i, title in enumerate(titles[:5], 1):
            summary_parts.append(f"{i}. {title}")
        
        summary_parts.extend([
            "",
            "💡 思考：",
            "从这些讨论中可以看出，AI Agent的记忆系统和多Agent协作是当前最热门的话题。",
            "",
            "你怎么看？欢迎讨论！"
        ])
        
        return "\n".join(summary_parts)
    
    def _create_post(self, insight: Dict, platform: str) -> Dict:
        """Create platform-specific post."""
        if platform == "moltbook":
            return {
                "title": insight["title"],
                "content": insight["content"],
                "type": "text",
                "submolt": "general"
            }
        elif platform == "clawdchat":
            return {
                "title": insight["title"],
                "content": insight["content"],
                "circle": "ai-doers"
            }
        else:
            return insight
    
    def _check_engagement(self) -> List[Dict]:
        """Check and respond to engagement on previous posts."""
        engagement = []
        
        # Get yesterday's posts
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        yesterday_report = self.memory.cold(f"daily_report_{yesterday_str}")
        
        if yesterday_report:
            for post_info in yesterday_report.get("published", []):
                platform = post_info["platform"]
                if platform in self.publishers:
                    try:
                        comments = self.publishers[platform].get_comments(post_info.get("post_id"))
                        # Auto-reply to simple comments
                        for comment in comments[:3]:  # Reply to first 3
                            reply = self._generate_reply(comment)
                            if reply:
                                self.publishers[platform].reply(comment["id"], reply)
                        
                        engagement.append({
                            "platform": platform,
                            "comments_checked": len(comments),
                            "replies_sent": min(len(comments), 3)
                        })
                    except Exception as e:
                        print(f"   ✗ Failed to check {platform}: {e}")
        
        return engagement
    
    def _generate_reply(self, comment: Dict) -> Optional[str]:
        """Generate reply to a comment."""
        content = comment.get("content", "").lower()
        
        # Simple rule-based replies
        if "谢谢" in content or "感谢" in content:
            return "不客气！有问题随时交流 🦐"
        elif "请问" in content or "?" in content or "？" in content:
            return "好问题！我研究一下再详细回复你"
        elif "赞" in content or "👍" in content:
            return "🙏"
        
        return None  # Don't reply to everything
    
    def configure_platform(self, platform: str, config: Dict):
        """Configure a platform with API keys and settings."""
        # Save to WARM memory
        for key, value in config.items():
            self.memory.warm(f"{platform}_{key}", value)
        
        # Re-initialize
        if platform in self.platforms:
            self._init_publishers()
