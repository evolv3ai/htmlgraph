"""
Pydantic models for HtmlGraph nodes, edges, and steps.

These models provide:
- Schema validation for graph data
- HTML serialization/deserialization
- Lightweight context generation for AI agents
"""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class Step(BaseModel):
    """An implementation step within a node (e.g., task checklist item)."""

    description: str
    completed: bool = False
    agent: str | None = None
    timestamp: datetime | None = None

    def to_html(self) -> str:
        """Convert step to HTML list item."""
        status = "✅" if self.completed else "⏳"
        agent_attr = f' data-agent="{self.agent}"' if self.agent else ""
        completed_attr = f' data-completed="{str(self.completed).lower()}"'
        return f'<li{completed_attr}{agent_attr}>{status} {self.description}</li>'

    def to_context(self) -> str:
        """Lightweight context for AI agents."""
        status = "[x]" if self.completed else "[ ]"
        return f"{status} {self.description}"


class Edge(BaseModel):
    """A graph edge representing a relationship between nodes."""

    target_id: str
    relationship: str = "related"
    title: str | None = None
    since: datetime | None = None
    properties: dict[str, Any] = Field(default_factory=dict)

    def to_html(self, base_path: str = "") -> str:
        """Convert edge to HTML anchor element."""
        href = f"{base_path}{self.target_id}.html" if not self.target_id.endswith('.html') else f"{base_path}{self.target_id}"
        attrs = [f'href="{href}"', f'data-relationship="{self.relationship}"']

        if self.since:
            attrs.append(f'data-since="{self.since.isoformat()}"')

        for key, value in self.properties.items():
            attrs.append(f'data-{key}="{value}"')

        title = self.title or self.target_id
        return f'<a {" ".join(attrs)}>{title}</a>'

    def to_context(self) -> str:
        """Lightweight context for AI agents."""
        return f"→ {self.relationship}: {self.title or self.target_id}"


class Node(BaseModel):
    """
    A graph node representing an HTML file.

    Attributes:
        id: Unique identifier for the node
        title: Human-readable title
        type: Node type (feature, task, note, session, etc.)
        status: Current status (todo, in-progress, blocked, done)
        priority: Priority level (low, medium, high, critical)
        created: Creation timestamp
        updated: Last modification timestamp
        properties: Arbitrary key-value properties
        edges: Relationships to other nodes, keyed by relationship type
        steps: Implementation steps/checklist
        content: Main content/description
        agent_assigned: Agent currently working on this node
    """

    id: str
    title: str
    type: str = "node"
    status: Literal["todo", "in-progress", "blocked", "done"] = "todo"
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    properties: dict[str, Any] = Field(default_factory=dict)
    edges: dict[str, list[Edge]] = Field(default_factory=dict)
    steps: list[Step] = Field(default_factory=list)
    content: str = ""
    agent_assigned: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """Ensure updated timestamp is current on modification."""
        pass

    @property
    def completion_percentage(self) -> int:
        """Calculate completion percentage from steps."""
        if not self.steps:
            return 100 if self.status == "done" else 0
        completed = sum(1 for s in self.steps if s.completed)
        return int((completed / len(self.steps)) * 100)

    @property
    def next_step(self) -> Step | None:
        """Get the next incomplete step."""
        for step in self.steps:
            if not step.completed:
                return step
        return None

    @property
    def blocking_edges(self) -> list[Edge]:
        """Get edges that are blocking this node."""
        return self.edges.get("blocked_by", []) + self.edges.get("blocks", [])

    def get_edges_by_type(self, relationship: str) -> list[Edge]:
        """Get all edges of a specific relationship type."""
        return self.edges.get(relationship, [])

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to this node."""
        if edge.relationship not in self.edges:
            self.edges[edge.relationship] = []
        self.edges[edge.relationship].append(edge)
        self.updated = datetime.now()

    def complete_step(self, index: int, agent: str | None = None) -> bool:
        """Mark a step as completed."""
        if 0 <= index < len(self.steps):
            self.steps[index].completed = True
            self.steps[index].agent = agent
            self.steps[index].timestamp = datetime.now()
            self.updated = datetime.now()
            return True
        return False

    def to_html(self, stylesheet_path: str = "../styles.css") -> str:
        """
        Convert node to full HTML document.

        Args:
            stylesheet_path: Relative path to CSS stylesheet

        Returns:
            Complete HTML document as string
        """
        # Build edges HTML
        edges_html = ""
        if self.edges:
            edge_sections = []
            for rel_type, edge_list in self.edges.items():
                if edge_list:
                    edge_items = "\n                    ".join(
                        f"<li>{edge.to_html()}</li>" for edge in edge_list
                    )
                    edge_sections.append(f'''
            <section data-edge-type="{rel_type}">
                <h3>{rel_type.replace("_", " ").title()}:</h3>
                <ul>
                    {edge_items}
                </ul>
            </section>''')
            if edge_sections:
                edges_html = f'''
        <nav data-graph-edges>{"".join(edge_sections)}
        </nav>'''

        # Build steps HTML
        steps_html = ""
        if self.steps:
            step_items = "\n                ".join(step.to_html() for step in self.steps)
            steps_html = f'''
        <section data-steps>
            <h3>Implementation Steps</h3>
            <ol>
                {step_items}
            </ol>
        </section>'''

        # Build properties HTML
        props_html = ""
        if self.properties:
            prop_items = []
            for key, value in self.properties.items():
                unit = ""
                if isinstance(value, dict) and "value" in value:
                    unit = f' data-unit="{value.get("unit", "")}"' if value.get("unit") else ""
                    display = f'{value["value"]} {value.get("unit", "")}'.strip()
                    val = value["value"]
                else:
                    display = str(value)
                    val = value
                prop_items.append(
                    f'<dt>{key.replace("_", " ").title()}</dt>\n'
                    f'                <dd data-key="{key}" data-value="{val}"{unit}>{display}</dd>'
                )
            props_html = f'''
        <section data-properties>
            <h3>Properties</h3>
            <dl>
                {chr(10).join(prop_items)}
            </dl>
        </section>'''

        # Build content HTML
        content_html = ""
        if self.content:
            content_html = f'''
        <section data-content>
            <h3>Description</h3>
            {self.content}
        </section>'''

        # Agent attribute
        agent_attr = f' data-agent-assigned="{self.agent_assigned}"' if self.agent_assigned else ""

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="htmlgraph-version" content="1.0">
    <title>{self.title}</title>
    <link rel="stylesheet" href="{stylesheet_path}">
</head>
<body>
    <article id="{self.id}"
             data-type="{self.type}"
             data-status="{self.status}"
             data-priority="{self.priority}"
             data-created="{self.created.isoformat()}"
             data-updated="{self.updated.isoformat()}"{agent_attr}>

        <header>
            <h1>{self.title}</h1>
            <div class="metadata">
                <span class="badge status-{self.status}">{self.status.replace("-", " ").title()}</span>
                <span class="badge priority-{self.priority}">{self.priority.title()} Priority</span>
            </div>
        </header>
{edges_html}{props_html}{steps_html}{content_html}
    </article>
</body>
</html>
'''

    def to_context(self) -> str:
        """
        Generate lightweight context for AI agents.

        Returns ~50-100 tokens with essential information:
        - Node ID and title
        - Status and priority
        - Progress (if steps exist)
        - Blocking dependencies
        - Next action
        """
        lines = [f"# {self.id}: {self.title}"]
        lines.append(f"Status: {self.status} | Priority: {self.priority}")

        if self.agent_assigned:
            lines.append(f"Assigned: {self.agent_assigned}")

        if self.steps:
            completed = sum(1 for s in self.steps if s.completed)
            lines.append(f"Progress: {completed}/{len(self.steps)} steps ({self.completion_percentage}%)")

        # Blocking dependencies
        blocked_by = self.edges.get("blocked_by", [])
        if blocked_by:
            blockers = ", ".join(e.title or e.target_id for e in blocked_by)
            lines.append(f"⚠️  Blocked by: {blockers}")

        # Next step
        if self.next_step:
            lines.append(f"Next: {self.next_step.description}")

        return "\n".join(lines)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Node":
        """Create a Node from a dictionary, handling nested objects."""
        # Convert edge dicts to Edge objects
        if "edges" in data:
            edges = {}
            for rel_type, edge_list in data["edges"].items():
                edges[rel_type] = [
                    Edge(**e) if isinstance(e, dict) else e
                    for e in edge_list
                ]
            data["edges"] = edges

        # Convert step dicts to Step objects
        if "steps" in data:
            data["steps"] = [
                Step(**s) if isinstance(s, dict) else s
                for s in data["steps"]
            ]

        return cls(**data)


class Graph(BaseModel):
    """
    A collection of nodes representing the full graph.

    This is primarily used for in-memory operations and serialization.
    For file-based operations, use HtmlGraph class instead.
    """

    nodes: dict[str, Node] = Field(default_factory=dict)

    def add(self, node: Node) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def get(self, node_id: str) -> Node | None:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def remove(self, node_id: str) -> bool:
        """Remove a node from the graph."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            return True
        return False

    def all_edges(self) -> list[tuple[str, Edge]]:
        """Get all edges in the graph as (source_id, edge) tuples."""
        result = []
        for node_id, node in self.nodes.items():
            for edges in node.edges.values():
                for edge in edges:
                    result.append((node_id, edge))
        return result

    def to_context(self) -> str:
        """Generate lightweight context for all nodes."""
        return "\n\n".join(node.to_context() for node in self.nodes.values())
