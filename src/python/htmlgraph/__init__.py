"""
HtmlGraph - HTML is All You Need

A lightweight graph database framework using HTML files as nodes,
hyperlinks as edges, and CSS selectors as the query language.
"""

from htmlgraph.models import Node, Edge, Step, Graph
from htmlgraph.graph import HtmlGraph
from htmlgraph.agents import AgentInterface
from htmlgraph.server import serve

__version__ = "0.1.0"
__all__ = [
    "Node",
    "Edge",
    "Step",
    "Graph",
    "HtmlGraph",
    "AgentInterface",
    "serve",
]
