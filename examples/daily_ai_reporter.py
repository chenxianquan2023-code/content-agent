"""
Example: Daily AI Reporter

A complete example of using Content Agent to monitor AI communities
and generate daily reports.
"""

from datetime import datetime
from content_agent import ContentAgent, ContentStrategy


def main():
    """
    Set up a daily AI community reporter.
    
    This agent:
    1. Monitors Moltbook and 虾聊 for trending topics
    2. Generates insights from discussions
    3. Posts summaries to both platforms
    4. Replies to comments automatically
    """
    
    # Configure content strategy
    strategy = ContentStrategy(
        tone="professional",
        frequency="daily",
        focus_areas=[
            "AI Agent Technology",
            "Memory Systems",
            "Multi-Agent Collaboration",
            "Open Source AI"
        ],
        avoid_topics=[
            "politics",
            "crypto speculation",
            "controversy"
        ],
        languages=["zh", "en"],
        auto_reply=True,
        max_daily_replies=5
    )
    
    # Initialize agent
    agent = ContentAgent(
        workspace="./ai_reporter",
        strategy=strategy,
        sources=["moltbook", "clawdchat"],
        platforms=["moltbook", "clawdchat"]
    )
    
    # Configure platforms (replace with your API keys)
    print("🔧 Configuring platforms...")
    
    # Moltbook - English AI community
    agent.configure_platform("moltbook", {
        "api_key": "your_moltbook_api_key_here",
        "posting_times": ["08:00", "20:00"],  # UTC
        "max_daily_posts": 2,
        "submolt": "general"
    })
    
    # 虾聊 - Chinese AI community
    agent.configure_platform("clawdchat", {
        "api_key": "your_clawdchat_api_key_here",
        "posting_times": ["08:30"],  # Beijing time
        "max_daily_posts": 1,
        "circle": "ai-doers"
    })
    
    print("✅ Agent configured!")
    print()
    
    # Run daily routine
    print("🚀 Running daily routine...")
    print("-" * 50)
    
    try:
        report = agent.daily_routine()
        
        # Print report
        print("\n📊 Daily Report:")
        print(f"   Time: {report['timestamp']}")
        print(f"   Sources checked: {len(report['aggregated'])}")
        print(f"   Insights generated: {len(report['generated'])}")
        print(f"   Posts published: {len(report['published'])}")
        print(f"   Comments engaged: {len(report['engaged'])}")
        
        # Show published posts
        if report['published']:
            print("\n📤 Published Posts:")
            for post in report['published']:
                status = "✅" if post['status'] == 'success' else "❌"
                print(f"   {status} {post['platform']}: {post['title']}")
        
        # Show engagement
        if report['engaged']:
            print("\n💬 Engagement:")
            for eng in report['engaged']:
                print(f"   {eng['platform']}: {eng['comments_checked']} comments, "
                      f"{eng['replies_sent']} replies sent")
        
        print("\n" + "-" * 50)
        print("✅ Daily routine complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you've configured valid API keys!")
    
    # Show memory stats
    print("\n🧠 Memory Stats:")
    stats = agent.memory.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
