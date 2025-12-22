"""
HtmlGraph - HTML is All You Need

A lightweight graph database framework using HTML files as nodes,
hyperlinks as edges, and CSS selectors as the query language.
"""

from htmlgraph.models import Node, Edge, Step, Graph, Session, ActivityEntry
from htmlgraph.graph import HtmlGraph
from htmlgraph.agents import AgentInterface
from htmlgraph.server import serve
from htmlgraph.session_manager import SessionManager
from htmlgraph.sdk import SDK
from htmlgraph.ids import generate_id, generate_hierarchical_id, parse_id, is_valid_id, is_legacy_id

__version__ = "0.4.0"
__all__ = [
    # Core models
    "Node",
    "Edge",
    "Step",
    "Graph",
    "Session",
    "ActivityEntry",
    # Graph operations
    "HtmlGraph",
    "AgentInterface",
    "SessionManager",
    "SDK",
    "serve",
    # ID generation (collision-resistant, multi-agent safe)
    "generate_id",
    "generate_hierarchical_id",
    "parse_id",
    "is_valid_id",
    "is_legacy_id",
]
