"""
Content Agent - AI-powered content curation and publishing.
Built on Agent Memory Kit.
"""

__version__ = "0.2.0"

from .agent import ContentAgent
from .strategy import ContentStrategy
from .llm.generator import ContentGenerator, GenerationConfig

try:
    from .web.dashboard import ContentDashboard, launch_dashboard
    HAS_DASHBOARD = True
except ImportError:
    HAS_DASHBOARD = False

__all__ = [
    "ContentAgent",
    "ContentStrategy", 
    "ContentGenerator",
    "GenerationConfig",
]

if HAS_DASHBOARD:
    __all__.extend(["ContentDashboard", "launch_dashboard"])
