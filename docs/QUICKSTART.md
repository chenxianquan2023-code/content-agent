# Quick Start Guide

Get up and running with Content Agent in 5 minutes.

## Installation

```bash
# Install agent-memory-kit first
pip install agent-memory-kit

# Then install content-agent
pip install content-agent
```

## Basic Setup

### 1. Create a Configuration File

Create `config.yaml`:

```yaml
sources:
  moltbook:
    enabled: true
    api_key: your_moltbook_api_key
  
  clawdchat:
    enabled: true
    api_key: your_clawdchat_api_key

platforms:
  moltbook:
    enabled: true
    max_posts: 2
  
  clawdchat:
    enabled: true
    max_posts: 1

content:
  strategy:
    tone: "professional"
    focus_areas: ["AI", "Technology"]
    languages: ["zh", "en"]
```

### 2. Run Your First Routine

```python
from content_agent import ContentAgent

# Load from config
agent = ContentAgent.from_config("config.yaml")

# Run daily routine
report = agent.daily_routine()

print(f"Published {len(report['published'])} posts!")
```

## Environment Variables

Instead of config file, you can use environment variables:

```bash
export MOLTBOOK_API_KEY="your_key"
export CLAWDCHAT_API_KEY="your_key"
```

Then in Python:

```python
import os
from content_agent import ContentAgent

agent = ContentAgent()
agent.configure_platform("moltbook", {
    "api_key": os.getenv("MOLTBOOK_API_KEY")
})
```

## What's Next?

- Read the [main README](../README.md) for full features
- Check [examples](../examples/) for real-world usage
- Configure your content [strategy](../README.md#advanced-configuration)

## Troubleshooting

### Import Error

If you get `ImportError: agent_memory_kit not found`:

```bash
# Make sure agent-memory-kit is installed
pip install agent-memory-kit

# Or if developing locally, ensure both repos are in sibling directories
```

### API Key Issues

If posts fail with authentication errors:
- Check your API keys are valid
- Verify keys are correctly set in config or environment
- Test keys manually with curl

### No Content Found

If no content is aggregated:
- Check your sources are enabled
- Verify API keys have read permissions
- Check filters aren't too restrictive
