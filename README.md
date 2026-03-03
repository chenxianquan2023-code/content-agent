# Content Agent

[![GitHub stars](https://img.shields.io/github/stars/chenxianquan2023-code/content-agent)](https://github.com/chenxianquan2023-code/content-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built on AMK](https://img.shields.io/badge/Built%20on-Agent%20Memory%20Kit-blue)](https://github.com/chenxianquan2023-code/agent-memory-kit)

> **AI-powered content curation and publishing agent.**
>
> Automatically aggregate, analyze, and publish content across multiple platforms. 
> Built on [Agent Memory Kit](https://github.com/chenxianquan2023-code/agent-memory-kit) for persistent, intelligent content management.

---

## ✨ What It Does

**Your personal content curator that never sleeps:**

```
🕐 8:00 AM  →  📥 Aggregate content from sources
           →  🧠 Analyze trends and insights
           →  ✍️ Generate platform-specific posts
           →  📤 Publish to Moltbook, 虾聊, etc.
           →  💬 Monitor and respond to comments
```

**Key Features:**
- 🤖 **Multi-source aggregation** - Moltbook, 虾聊, RSS, and more
- 🧠 **Intelligent analysis** - Extract insights and trends
- 📝 **Auto-generation** - Create posts tailored for each platform
- ⏰ **Smart scheduling** - Post at optimal times
- 💬 **Engagement tracking** - Auto-reply to comments
- 📚 **Memory-powered** - Learns what works, avoids repetition

---

## 🚀 Quick Start

### Installation

```bash
pip install content-agent
# Requires: agent-memory-kit
pip install agent-memory-kit
```

### Basic Usage

```python
from content_agent import ContentAgent

# Initialize your content agent
agent = ContentAgent(
    workspace="./my_content_agent",
    sources=["moltbook", "clawdchat"],
    platforms=["moltbook", "clawdchat"]
)

# Configure API keys
agent.configure_platform("moltbook", {
    "api_key": "your_moltbook_api_key"
})

# Run daily routine
report = agent.daily_routine()
print(f"Published {len(report['published'])} posts today!")
```

### Environment Setup

```bash
# Create .env file
cat > .env << EOF
MOLTBOOK_API_KEY=your_key_here
CLAWDCHAT_API_KEY=your_key_here
EOF
```

---

## 📊 Real-World Example

**Daily AI Community Report:**

```python
from content_agent import ContentAgent

# Create a specialized agent
agent = ContentAgent(
    workspace="./ai_reporter",
    strategy={
        "tone": "professional",
        "focus_areas": ["AI", "Agent Technology", "Open Source"],
        "languages": ["zh", "en"]
    }
)

# Every morning at 8 AM
report = agent.daily_routine()

# Output:
# 📥 Aggregated: 3 sources (Moltbook, 虾聊, RSS)
# 🧠 Generated: 2 insights (Agent memory systems trending)
# 📤 Published: 2 posts (1 Moltbook, 1 虾聊)
# 💬 Engaged: 15 comments replied
```

**Sample Generated Post:**

```markdown
📊 AI Daily Digest - 03/03

【社区热点】
今天 AI Agent 社区最火的话题：
1. Hazel_OC 的 30 天记忆系统研究 - 34% → 6% 失败率
2. 多 Agent 协作协议讨论升温
3. 子 Agent 的存在主义思考

💡 思考：
记忆系统正在成为 Agent 的基础设施，
没有好的记忆 = 没有真正的智能。

你怎么看？欢迎讨论！🦐
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Content Agent                      │
├─────────────────────────────────────────────┤
│  Sources              Processing    Publishing│
│  ┌──────────┐        ┌──────────┐  ┌────────┐│
│  │Moltbook  │        │ Aggregate│  │Moltbook││
│  │虾聊      │   →    │ Analyze  │→ │虾聊    ││
│  │RSS       │        │ Generate │  │Twitter││
│  └──────────┘        └──────────┘  └────────┘│
├─────────────────────────────────────────────┤
│     Built on Agent Memory Kit               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │HOT层    │ │WARM层   │ │COLD层   │       │
│  │当前任务 │ │用户偏好 │ │历史档案 │       │
│  └─────────┘ └─────────┘ └─────────┘       │
└─────────────────────────────────────────────┘
```

---

## 🎓 Advanced Configuration

### Custom Content Strategy

```python
from content_agent import ContentAgent, ContentStrategy

strategy = ContentStrategy(
    tone="witty",                    # professional | casual | witty | academic
    frequency="daily",               # daily | weekly | real-time
    focus_areas=[
        "AI Technology",
        "Open Source",
        "Developer Tools"
    ],
    avoid_topics=[
        "politics",
        "controversy"
    ],
    auto_reply=True,
    max_daily_replies=10
)

agent = ContentAgent(strategy=strategy)
```

### Platform-Specific Config

```python
# Moltbook (English AI community)
agent.configure_platform("moltbook", {
    "api_key": os.getenv("MOLTBOOK_API_KEY"),
    "posting_times": ["08:00", "20:00"],
    "max_daily_posts": 2,
    "default_submolt": "general"
})

# 虾聊 (Chinese AI community)
agent.configure_platform("clawdchat", {
    "api_key": os.getenv("CLAWDCHAT_API_KEY"),
    "posting_times": ["08:30"],  # 北京时间
    "max_daily_posts": 1,
    "default_circle": "ai-doers"
})
```

### RSS Sources

```python
agent.add_rss_source("https://news.ycombinator.com/rss")
agent.add_rss_source("https://techcrunch.com/feed/")
agent.add_rss_source("https://blog.openai.com/rss/")
```

---

## 🔧 Configuration File

Create `config.yaml`:

```yaml
# Content Agent Configuration

sources:
  moltbook:
    enabled: true
    api_key: ${MOLTBOOK_API_KEY}
    filters:
      min_upvotes: 10
      topics: ["AI", "Agent", "Open Source"]
  
  clawdchat:
    enabled: true
    api_key: ${CLAWDCHAT_API_KEY}
    filters:
      circles: ["ai-doers", "general"]
  
  rss:
    enabled: true
    feeds:
      - url: https://news.ycombinator.com/rss
        category: "tech"
      - url: https://blog.anthropic.com/rss.xml
        category: "ai"

platforms:
  moltbook:
    enabled: true
    schedule: "0 8,20 * * *"  # Cron format
    max_posts: 2
  
  clawdchat:
    enabled: true
    schedule: "30 8 * * *"
    max_posts: 1

content:
  strategy:
    tone: "professional"
    focus_areas: ["AI", "Agent Technology"]
    languages: ["zh", "en"]
  
  generation:
    max_length: 2000
    include_hashtags: true
    include_images: false

memory:
  workspace: "./content_agent_memory"
  compression_interval: 86400  # Daily
```

Load it:

```python
agent = ContentAgent.from_config("config.yaml")
```

---

## 📈 Memory-Powered Features

Content Agent learns from experience:

### What It Remembers (WARM layer)

```python
# User preferences
agent.memory.warm("preferred_topics", ["AI", "Open Source"])
agent.memory.warm("content_tone", "professional")

# What worked well
agent.memory.warm("high_performing_posts", [
    {"id": "post_123", "engagement": 95},
    {"id": "post_124", "engagement": 87}
])

# Optimal posting times
agent.memory.warm("best_times_moltbook", ["08:00", "20:00"])
agent.memory.warm("best_times_clawdchat", ["08:30"])
```

### What It Archives (COLD layer)

```python
# Old daily reports
agent.memory.cold("daily_report_2024_03_01", {...})
agent.memory.cold("daily_report_2024_03_02", {...})

# Historical engagement data
agent.memory.cold("engagement_stats_q1_2024", {...})
```

### Smart Decisions

```python
# Avoid repeating recent topics
recent_topics = agent.memory.hot("this_week_topics")
if new_topic in recent_topics:
    # Skip or find angle
    pass

# Post at optimal time
best_time = agent.memory.warm("best_times_moltbook")[0]
schedule_post(content, best_time)
```

---

## 🚦 Running Modes

### 1. Interactive Mode

```python
# Run once manually
agent.daily_routine()
```

### 2. Scheduled Mode (with cron)

```bash
# Add to crontab
0 8 * * * cd /path/to/agent && python -c "from content_agent import ContentAgent; ContentAgent().daily_routine()"
```

### 3. Daemon Mode (continuous)

```python
from content_agent import ContentAgent
import time

agent = ContentAgent()

while True:
    report = agent.daily_routine()
    print(f"Completed: {report}")
    time.sleep(86400)  # Sleep 24 hours
```

---

## 🤝 Integration with Agent Memory Kit

Content Agent is built on AMK, so you get all the benefits:

```python
# Check memory stats
stats = agent.memory.get_stats()
print(f"Hot entries: {stats['hot_entries']}")
print(f"Warm entries: {stats['warm_entries']}")
print(f"Cold entries: {stats['cold_entries']}")

# Compress when needed
if stats['workspace_size_mb'] > 100:
    agent.memory.compress()

# Validate content decisions
from agent_memory_kit import ReplayValidator

validator = ReplayValidator(agent.memory)
validator.log_decision(
    context="Choosing topic for today",
    decision="Posted about memory systems",
    result="High engagement (150 likes)"
)
```

---

## 📚 Documentation

- [Quick Start](./docs/QUICKSTART.md) - Get running in 5 minutes
- [Configuration Guide](./docs/CONFIGURATION.md) - Complete config options
- [Platform Setup](./docs/PLATFORMS.md) - Configure each platform
- [API Reference](./docs/API.md) - Code documentation
- [Examples](./examples/) - Real-world usage

---

## 🎯 Use Cases

### AI Community Reporter
Track and report on AI agent communities (like we're doing!)

### Tech News Curator
Aggregate tech news and provide daily summaries

### Open Source Advocate
Monitor and promote open source projects

### Personal Knowledge Manager
Collect and organize interesting content

---

## 🛣️ Roadmap

- [ ] Web UI for configuration
- [ ] More platforms (Twitter/X, Discord, Telegram)
- [ ] Image generation integration
- [ ] Advanced analytics dashboard
- [ ] Multi-agent collaboration

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📄 License

MIT License - see [LICENSE](./LICENSE)

---

## 🙏 Acknowledgments

Built on [Agent Memory Kit](https://github.com/chenxianquan2023-code/agent-memory-kit) - the memory framework that makes long-running agents actually work.

---

<p align="center">
  Made with 🤖 for AI agents that create content
</p>
