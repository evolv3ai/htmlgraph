"""
Analytics modules for HtmlGraph.

Provides work type analysis, dependency analytics, cross-session analytics, and CLI analytics.
"""

from htmlgraph.analytics.cross_session import CrossSessionAnalytics
from htmlgraph.analytics.dependency import DependencyAnalytics
from htmlgraph.analytics.work_type import Analytics

__all__ = [
    "Analytics",
    "DependencyAnalytics",
    "CrossSessionAnalytics",
]
