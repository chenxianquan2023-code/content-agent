"""
Content Agent - AI-powered content curation and publishing.
Built on Agent Memory Kit.
"""

__version__ = "0.1.0"

from .agent import ContentAgent
from .sources import MoltbookSource, ClawdchatSource, RSSSource
from .publisher import MoltbookPublisher, ClawdchatPublisher
from .strategy import ContentStrategy

__all__ = [
    "ContentAgent",
    "MoltbookSource",
    "ClawdchatSource", 
    "RSSSource",
    "MoltbookPublisher",
    "ClawdchatPublisher",
    "ContentStrategy"
]
