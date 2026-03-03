"""
LLM integration for content generation.
Supports OpenAI, Claude, and local models.
"""

import json
import urllib.request
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """Configuration for content generation."""
    model: str = "claude-sonnet-4-6"
    temperature: float = 0.7
    max_tokens: int = 2000
    style: str = "professional"  # professional | casual | witty
    language: str = "zh"


class LLMClient:
    """Base class for LLM clients."""
    
    def generate(self, prompt: str, config: GenerationConfig) -> str:
        raise NotImplementedError


class ClaudeClient(LLMClient):
    """Anthropic Claude API client."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"
    
    def generate(self, prompt: str, config: GenerationConfig) -> str:
        """Generate content using Claude."""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        req = urllib.request.Request(
            f"{self.base_url}/messages",
            data=json.dumps(data).encode(),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode())
                return result["content"][0]["text"]
        except Exception as e:
            raise Exception(f"Claude API error: {e}")


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    def generate(self, prompt: str, config: GenerationConfig) -> str:
        """Generate content using OpenAI."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature
        }
        
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(data).encode(),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode())
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")


class ContentGenerator:
    """
    Content generation using LLMs.
    
    Features:
    - Summarize multiple posts
    - Generate insights
    - Create platform-specific content
    - Translate between languages
    """
    
    def __init__(self, provider: str = "claude", api_key: str = None):
        if provider == "claude":
            self.client = ClaudeClient(api_key)
        elif provider == "openai":
            self.client = OpenAIClient(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        self.config = GenerationConfig()
    
    def summarize_posts(self, posts: List[Dict], 
                        max_length: str = "medium") -> str:
        """
        Summarize multiple posts into a digest.
        
        Args:
            posts: List of post dictionaries
            max_length: short | medium | long
            
        Returns:
            Summarized content
        """
        # Prepare post summaries
        post_texts = []
        for i, post in enumerate(posts[:10], 1):
            text = f"{i}. {post.get('title', '')}\n{post.get('content', '')[:200]}..."
            post_texts.append(text)
        
        posts_str = "\n\n".join(post_texts)
        
        word_counts = {"short": 200, "medium": 500, "long": 1000}
        target_words = word_counts.get(max_length, 500)
        
        prompt = f"""请总结以下AI社区讨论，生成一份{target_words}字左右的日报：

{posts_str}

要求：
1. 提取3-5个核心话题
2. 每个话题给出简要分析和观点
3. 最后加一个开放式问题引发讨论
4. 使用专业但易懂的语言
5. 适当使用emoji增加可读性

请用中文输出。"""
        
        self.config.language = "zh"
        return self.client.generate(prompt, self.config)
    
    def generate_insight(self, topic: str, 
                        context: List[str]) -> str:
        """
        Generate deep insight on a topic.
        
        Args:
            topic: Topic to analyze
            context: Supporting context points
            
        Returns:
            Insightful analysis
        """
        context_str = "\n".join([f"- {c}" for c in context])
        
        prompt = f"""基于以下信息，对"{topic}"进行深入分析：

背景信息：
{context_str}

请提供：
1. 核心观点（2-3句话）
2. 深度分析（为什么重要）
3. 实际影响（对AI社区意味着什么）
4. 未来展望（可能的发展方向）

字数：400-600字
风格：专业、有洞察力、引发思考"""
        
        return self.client.generate(prompt, self.config)
    
    def create_platform_post(self, content: str,
                            platform: str,
                            tone: str = "professional") -> str:
        """
        Adapt content for specific platform.
        
        Args:
            content: Source content
            platform: moltbook | clawdchat | twitter
            tone: writing tone
            
        Returns:
            Platform-optimized content
        """
        platform_guides = {
            "moltbook": "英文技术社区，专业、详细、欢迎深度讨论",
            "clawdchat": "中文AI社区，亲切、实用、鼓励互动",
            "twitter": "简短精炼，重点突出，适合快速传播"
        }
        
        guide = platform_guides.get(platform, "通用")
        
        prompt = f"""请将以下内容改写为适合{platform}平台的格式：

原始内容：
{content}

平台特点：{guide}

要求：
1. 保持核心信息完整
2. 调整语言风格适配平台
3. 优化格式（段落、列表等）
4. 添加合适的hashtag或话题标签

直接输出改写后的内容，不要解释。"""
        
        return self.client.generate(prompt, self.config)
    
    def generate_reply(self, comment: str,
                      context: Optional[str] = None) -> Optional[str]:
        """
        Generate reply to a comment.
        
        Args:
            comment: Comment text
            context: Optional conversation context
            
        Returns:
            Reply text or None if no reply needed
        """
        # Simple filter - don't reply to everything
        if len(comment) < 5:
            return None
        
        prompt = f"""请为以下评论生成一个友好的回复：

评论内容："{comment}"

{f"上下文：{context}" if context else ""}

要求：
1. 语气友好、专业
2. 回应评论中的观点或问题
3. 简短（2-3句话）
4. 适当使用emoji
5. 如果是简单点赞，回复"🙏"即可

直接输出回复内容："""
        
        return self.client.generate(prompt, self.config)
    
    def translate(self, text: str, 
                  target_lang: str) -> str:
        """Translate content between languages."""
        prompt = f"""请将以下内容翻译为{target_lang}：

{text}

要求：
1. 保持原意不变
2. 使用地道表达
3. 保留markdown格式
4. 专业术语准确

直接输出翻译结果："""
        
        return self.client.generate(prompt, self.config)
