"""
Content strategy configuration.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ContentStrategy:
    """Configuration for content generation strategy."""
    
    # Tone and style
    tone: str = "professional"  # professional | casual | witty | academic
    
    # Frequency
    frequency: str = "daily"  # daily | weekly | real-time
    
    # Content focus
    focus_areas: Optional[List[str]] = None
    avoid_topics: Optional[List[str]] = None
    
    # Language
    languages: Optional[List[str]] = None  # ["zh", "en"]
    
    # Engagement
    auto_reply: bool = True
    reply_tone: str = "friendly"
    max_daily_replies: int = 10
    
    # Quality thresholds
    min_post_length: int = 100
    max_post_length: int = 2000
    
    def __post_init__(self):
        if self.focus_areas is None:
            self.focus_areas = ["AI", "technology", "productivity"]
        if self.avoid_topics is None:
            self.avoid_topics = ["politics", "controversy", "sensitive"]
        if self.languages is None:
            self.languages = ["zh", "en"]
