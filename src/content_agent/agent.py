"""
Core Content Agent implementation with LLM and real APIs.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import from agent-memory-kit
try:
    from agent_memory_kit import MemoryManager
except ImportError:
    import sys
    amk_path = Path(__file__).parent.parent.parent.parent / "agent-memory-kit" / "src"
    if amk_path.exists():
        sys.path.insert(0, str(amk_path))
    from agent_memory_kit import MemoryManager

from .strategy import ContentStrategy
from .llm.generator import ContentGenerator, GenerationConfig


class ContentAgent:
    """
    AI-powered content curation and publishing agent.
    
    Features:
    - Real API integration (Moltbook, 虾聊)
    - LLM-powered content generation
    - Multi-source aggregation
    - Auto-engagement
    """
    
    def __init__(self, 
                 workspace: str = "./content_agent",
                 strategy: Optional[ContentStrategy] = None,
                 llm_provider: str = "claude",
                 llm_api_key: Optional[str] = None):
        
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Initialize memory
        self.memory = MemoryManager(workspace)
        
        # Content strategy
        self.strategy = strategy or ContentStrategy()
        
        # LLM for content generation
        self.generator = None
        if llm_api_key:
            self.generator = ContentGenerator(llm_provider, llm_api_key)
        
        # API clients (initialized on demand)
        self._sources = {}
        self._publishers = {}
    
    def _get_source(self, name: str):
        """Lazy load source."""
        if name not in self._sources:
            if name == "moltbook":
                from .sources.moltbook import MoltbookSource
                api_key = self.memory.warm("moltbook_api_key")
                if api_key:
                    self._sources[name] = MoltbookSource(api_key)
            elif name == "clawdchat":
                from .sources.clawdchat import ClawdchatSource
                api_key = self.memory.warm("clawdchat_api_key")
                if api_key:
                    self._sources[name] = ClawdchatSource(api_key)
        return self._sources.get(name)
    
    def _get_publisher(self, name: str):
        """Lazy load publisher."""
        if name not in self._publishers:
            if name == "moltbook":
                from .sources.moltbook import MoltbookPublisher
                api_key = self.memory.warm("moltbook_api_key")
                if api_key:
                    self._publishers[name] = MoltbookPublisher(api_key)
            elif name == "clawdchat":
                from .sources.clawdchat import ClawdchatPublisher
                api_key = self.memory.warm("clawdchat_api_key")
                if api_key:
                    self._publishers[name] = ClawdchatPublisher(api_key)
        return self._publishers.get(name)
    
    def daily_routine(self, sources: List[str] = None,
                     platforms: List[str] = None) -> Dict[str, Any]:
        """
        Execute daily content routine with LLM generation.
        """
        sources = sources or ["moltbook", "clawdchat"]
        platforms = platforms or ["moltbook", "clawdchat"]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "aggregated": [],
            "generated": [],
            "published": [],
            "engaged": []
        }
        
        # 1. Aggregate
        print("📥 Aggregating content...")
        all_posts = []
        for source_name in sources:
            source = self._get_source(source_name)
            if source:
                try:
                    posts = source.fetch_posts(limit=20)
                    all_posts.extend(posts)
                    report["aggregated"].append(f"{source_name}: {len(posts)} posts")
                    print(f"   ✓ {source_name}: {len(posts)} posts")
                except Exception as e:
                    print(f"   ✗ {source_name}: {e}")
        
        # 2. Generate with LLM
        if all_posts and self.generator:
            print("🧠 Generating content with LLM...")
            try:
                summary = self.generator.summarize_posts(all_posts, "medium")
                report["generated"].append("Daily digest")
                print(f"   ✓ Generated summary: {len(summary)} chars")
                
                # Publish to platforms
                for platform in platforms:
                    publisher = self._get_publisher(platform)
                    if publisher:
                        try:
                            # Adapt for platform
                            adapted = self.generator.create_platform_post(
                                summary, platform, self.strategy.tone
                            )
                            
                            # Publish
                            result = publisher.publish({
                                "title": f"AI Daily Digest - {datetime.now().strftime('%m/%d')}",
                                "content": adapted,
                                "submolt" if platform == "moltbook" else "circle": "general" if platform == "moltbook" else "ai-doers"
                            })
                            
                            report["published"].append({
                                "platform": platform,
                                "status": "success"
                            })
                            print(f"   ✓ Published to {platform}")
                            
                        except Exception as e:
                            report["published"].append({
                                "platform": platform,
                                "status": "failed",
                                "error": str(e)
                            })
                            print(f"   ✗ Failed to publish to {platform}: {e}")
        
        # Save report
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.memory.cold(f"daily_report_{date_str}", report)
        
        return report
    
    def configure_platform(self, platform: str, config: Dict):
        """Configure platform API keys."""
        for key, value in config.items():
            self.memory.warm(f"{platform}_{key}", value)
        # Clear cache to reload
        self._sources.pop(platform, None)
        self._publishers.pop(platform, None)
    
    def generate_insight(self, topic: str, 
                        context: List[str]) -> str:
        """Generate deep insight on topic."""
        if not self.generator:
            raise RuntimeError("LLM not configured")
        return self.generator.generate_insight(topic, context)
    
    def get_stats(self) -> Dict:
        """Get agent statistics."""
        return {
            "memory": self.memory.get_stats(),
            "sources": list(self._sources.keys()),
            "platforms": list(self._publishers.keys()),
            "llm_configured": self.generator is not None
        }
