# Content Agent

AI-powered content curation and publishing agent. Built on [Agent Memory Kit](https://github.com/YOUR_USERNAME/agent-memory-kit).

## 🎯 What It Does

Automatically curate, analyze, and publish content across multiple platforms.

**Daily Workflow:**
```
8:00 AM  →  Aggregate content from sources
         →  Generate insights and summaries  
         →  Create platform-specific posts
         →  Publish to Moltbook, 虾聊, etc.
         →  Monitor engagement and reply
```

## 🚀 Quick Start

```python
from content_agent import ContentAgent

# Initialize with your preferences
agent = ContentAgent(
    workspace="./my_content_agent",
    sources=["moltbook", "clawdchat", "rss"],
    platforms=["moltbook", "clawdchat"]
)

# Run daily routine
agent.daily_routine()
```

## 📊 Features

### Content Aggregation
- 🤖 **Moltbook** - AI community insights
- 🦐 **虾聊 (ClawdChat)** - Chinese AI community
- 📰 **RSS Feeds** - News and blogs
- 🔍 **Web Search** - Real-time information

### Content Generation
- 📝 **Summarization** - Extract key points
- 💡 **Insight Generation** - Find patterns and trends
- 🎨 **Multi-format** - Text, markdown, social posts

### Publishing
- 📤 **Multi-platform** - One content, multiple formats
- ⏰ **Scheduling** - Time-optimized posting
- 💬 **Engagement** - Auto-reply to comments

### Memory-Powered
Thanks to Agent Memory Kit:
- 📚 Learns your content preferences
- 🎯 Remembers what performed well
- 🔁 Avoids repeating topics
- 📈 Tracks engagement patterns

## 📦 Installation

```bash
pip install content-agent
```

## 🎓 Advanced Usage

### Custom Content Strategy

```python
from content_agent import ContentAgent, ContentStrategy

strategy = ContentStrategy(
    tone="professional",      # professional | casual | witty
    frequency="daily",        # daily | weekly | real-time
    focus_areas=["AI", "tech", "productivity"],
    avoid_topics=["politics", "controversy"]
)

agent = ContentAgent(strategy=strategy)
```

### Platform-Specific Config

```python
agent.configure_platform("moltbook", {
    "api_key": "your_key",
    "posting_times": ["08:00", "20:00"],
    "max_daily_posts": 2
})
```

## 🔧 Configuration

Create `config.yaml`:

```yaml
sources:
  moltbook:
    enabled: true
    api_key: ${MOLTBOOK_API_KEY}
  
  clawdchat:
    enabled: true
    api_key: ${CLAWDCHAT_API_KEY}
  
  rss:
    enabled: true
    feeds:
      - https://news.ycombinator.com/rss
      - https://techcrunch.com/feed

platforms:
  moltbook:
    enabled: true
    daily_limit: 2
  
  clawdchat:
    enabled: true
    daily_limit: 1

content:
  topics: ["AI", "tech", "productivity"]
  tone: "professional"
  language: ["zh", "en"]
```

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](./LICENSE)

## 🙏 Acknowledgments

Built with [Agent Memory Kit](https://github.com/YOUR_USERNAME/agent-memory-kit) - the memory framework that makes long-running agents actually work.
