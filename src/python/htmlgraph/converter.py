"""
Bidirectional converters between HTML files and Pydantic models.

Provides:
- html_to_node: Parse HTML file into Node model
- node_to_html: Write Node model to HTML file
- Preserves all semantic information
- Handles edge cases (missing fields, malformed HTML)
"""

from pathlib import Path
from typing import Any

from htmlgraph.models import Node, Edge, Step
from htmlgraph.parser import HtmlParser


def html_to_node(filepath: Path | str) -> Node:
    """
    Parse HTML file into a Node model.

    Args:
        filepath: Path to HTML file

    Returns:
        Node instance populated from HTML

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If HTML is malformed or missing required data
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"HTML file not found: {filepath}")

    parser = HtmlParser.from_file(filepath)
    data = parser.parse_full_node()

    # Validate required fields
    if not data.get("id"):
        raise ValueError(f"HTML file missing node ID: {filepath}")

    # Convert edge dicts to Edge models
    edges: dict[str, list[Edge]] = {}
    for rel_type, edge_list in data.get("edges", {}).items():
        edges[rel_type] = [
            Edge(
                target_id=e["target_id"],
                relationship=e.get("relationship", rel_type),
                title=e.get("title"),
                since=e.get("since"),
                properties=e.get("properties", {}),
            )
            for e in edge_list
        ]
    data["edges"] = edges

    # Convert step dicts to Step models
    steps = [
        Step(
            description=s["description"],
            completed=s.get("completed", False),
            agent=s.get("agent"),
        )
        for s in data.get("steps", [])
    ]
    data["steps"] = steps

    return Node(**data)


def node_to_html(
    node: Node,
    filepath: Path | str,
    stylesheet_path: str = "../styles.css",
    create_dirs: bool = True
) -> Path:
    """
    Write a Node model to an HTML file.

    Args:
        node: Node instance to serialize
        filepath: Destination file path
        stylesheet_path: Relative path to CSS stylesheet
        create_dirs: Create parent directories if needed

    Returns:
        Path to written file
    """
    filepath = Path(filepath)

    if create_dirs:
        filepath.parent.mkdir(parents=True, exist_ok=True)

    html_content = node.to_html(stylesheet_path=stylesheet_path)
    filepath.write_text(html_content, encoding="utf-8")

    return filepath


def update_node_html(
    filepath: Path | str,
    updates: dict[str, Any],
    stylesheet_path: str = "../styles.css"
) -> Node:
    """
    Update specific fields in an existing HTML node file.

    Args:
        filepath: Path to existing HTML file
        updates: Dict of fields to update
        stylesheet_path: Relative path to CSS stylesheet

    Returns:
        Updated Node instance

    Example:
        update_node_html("task.html", {"status": "done"})
    """
    # Load existing node
    node = html_to_node(filepath)

    # Apply updates
    for key, value in updates.items():
        if hasattr(node, key):
            setattr(node, key, value)

    # Write back
    node_to_html(node, filepath, stylesheet_path=stylesheet_path)

    return node


def merge_nodes(base: Node, overlay: Node) -> Node:
    """
    Merge two nodes, with overlay values taking precedence.

    Useful for updating nodes while preserving unspecified fields.

    Args:
        base: Base node with default values
        overlay: Node with values to apply over base

    Returns:
        New Node instance with merged values
    """
    base_dict = base.model_dump()
    overlay_dict = overlay.model_dump(exclude_unset=True)

    # Deep merge for nested structures
    for key, value in overlay_dict.items():
        if key == "edges" and value:
            # Merge edge dictionaries
            base_edges = base_dict.get("edges", {})
            for rel_type, edge_list in value.items():
                if rel_type in base_edges:
                    # Replace edges of same type
                    base_edges[rel_type] = edge_list
                else:
                    base_edges[rel_type] = edge_list
            base_dict["edges"] = base_edges
        elif key == "steps" and value:
            # Replace steps entirely
            base_dict["steps"] = value
        elif key == "properties" and value:
            # Merge properties
            base_dict.setdefault("properties", {}).update(value)
        else:
            base_dict[key] = value

    return Node.from_dict(base_dict)


def node_to_dict(node: Node) -> dict[str, Any]:
    """
    Convert Node to a plain dictionary (JSON-serializable).

    Useful for API responses or JSON export.
    """
    data = node.model_dump()

    # Convert datetime objects to ISO strings
    for key in ["created", "updated"]:
        if key in data and data[key]:
            data[key] = data[key].isoformat()

    # Convert edges
    for rel_type, edges in data.get("edges", {}).items():
        for edge in edges:
            if edge.get("since"):
                edge["since"] = edge["since"].isoformat()

    # Convert steps
    for step in data.get("steps", []):
        if step.get("timestamp"):
            step["timestamp"] = step["timestamp"].isoformat()

    return data


def dict_to_node(data: dict[str, Any]) -> Node:
    """
    Create Node from a plain dictionary.

    Handles datetime string parsing.
    """
    from datetime import datetime

    # Parse datetime strings
    for key in ["created", "updated"]:
        if key in data and isinstance(data[key], str):
            data[key] = datetime.fromisoformat(data[key].replace("Z", "+00:00"))

    # Parse edge datetimes
    for edges in data.get("edges", {}).values():
        for edge in edges:
            if isinstance(edge.get("since"), str):
                edge["since"] = datetime.fromisoformat(edge["since"].replace("Z", "+00:00"))

    # Parse step datetimes
    for step in data.get("steps", []):
        if isinstance(step.get("timestamp"), str):
            step["timestamp"] = datetime.fromisoformat(step["timestamp"].replace("Z", "+00:00"))

    return Node.from_dict(data)


class NodeConverter:
    """
    Converter class for batch operations on multiple nodes.

    Example:
        converter = NodeConverter("features/")
        nodes = converter.load_all()
        converter.save_all(nodes)
    """

    def __init__(self, directory: Path | str, stylesheet_path: str = "../styles.css"):
        """
        Initialize converter for a directory.

        Args:
            directory: Directory containing HTML node files
            stylesheet_path: Default stylesheet path for new files
        """
        self.directory = Path(directory)
        self.stylesheet_path = stylesheet_path

    def load(self, node_id: str) -> Node | None:
        """Load a single node by ID."""
        filepath = self.directory / f"{node_id}.html"
        if filepath.exists():
            return html_to_node(filepath)
        return None

    def load_all(self, pattern: str = "*.html") -> list[Node]:
        """Load all nodes matching pattern."""
        nodes = []
        for filepath in self.directory.glob(pattern):
            try:
                nodes.append(html_to_node(filepath))
            except (ValueError, KeyError):
                continue  # Skip malformed files
        return nodes

    def save(self, node: Node) -> Path:
        """Save a single node."""
        filepath = self.directory / f"{node.id}.html"
        return node_to_html(node, filepath, self.stylesheet_path)

    def save_all(self, nodes: list[Node]) -> list[Path]:
        """Save multiple nodes."""
        return [self.save(node) for node in nodes]

    def exists(self, node_id: str) -> bool:
        """Check if a node file exists."""
        return (self.directory / f"{node_id}.html").exists()

    def delete(self, node_id: str) -> bool:
        """Delete a node file."""
        filepath = self.directory / f"{node_id}.html"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
