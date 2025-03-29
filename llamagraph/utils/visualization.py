"""
Visualization utilities for LlamaGraph
"""
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import tempfile
import json
import os

import networkx as nx

logger = logging.getLogger(__name__)

# Check if matplotlib and matplotlib-inline are available
try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("Matplotlib not available. Some visualizations will be disabled.")

# Check if pyvis is available for interactive visualization
try:
    from pyvis.network import Network
    HAS_PYVIS = True
except ImportError:
    HAS_PYVIS = False
    logger.warning("Pyvis not available. Interactive visualizations will be disabled.")

# Check if plotly is available for 3D visualization
try:
    import plotly.graph_objects as go
    import plotly.io as pio
    import numpy as np
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    logger.warning("Plotly not available. 3D visualizations will be disabled.")


def plot_knowledge_graph(
    graph: nx.DiGraph,
    title: str = "Knowledge Graph",
    figsize: Tuple[int, int] = (12, 10),
    node_size: int = 1000,
    node_color_map: Optional[Dict[str, str]] = None,
    edge_color_map: Optional[Dict[str, str]] = None,
    save_path: Optional[Path] = None,
    show: bool = True
) -> Optional[plt.Figure]:
    """
    Plot a knowledge graph using matplotlib
    
    Args:
        graph: The NetworkX graph to plot
        title: The title of the plot
        figsize: The figure size (width, height) in inches
        node_size: The size of the nodes
        node_color_map: Mapping from node types to colors
        edge_color_map: Mapping from edge types to colors
        save_path: Path to save the figure
        show: Whether to show the figure
        
    Returns:
        The matplotlib figure if show is False, otherwise None
    """
    if not HAS_MATPLOTLIB:
        logger.error("Matplotlib is required for plotting. Install with pip install matplotlib")
        return None
        
    # Default color maps if not provided
    if node_color_map is None:
        node_color_map = {
            "PERSON": "skyblue",
            "ORG": "lightgreen",
            "GPE": "salmon",
            "LOC": "orange",
            "PRODUCT": "purple",
            "EVENT": "yellow",
            "WORK_OF_ART": "pink",
            "LAW": "brown",
            "LANGUAGE": "gray",
            "DATE": "cyan",
            "TIME": "lightblue",
            "MONEY": "green",
            "QUANTITY": "red",
            "PERCENT": "blue",
            "CARDINAL": "magenta",
            "ORDINAL": "teal"
        }
    
    # Create a layout
    pos = nx.spring_layout(graph, seed=42)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Extract node types and assign colors
    node_colors = []
    for node in graph.nodes():
        node_type = graph.nodes[node].get("entity_type", "UNKNOWN")
        node_colors.append(node_color_map.get(node_type, "gray"))
    
    # Draw nodes
    nx.draw_networkx_nodes(
        graph, pos, 
        node_size=node_size,
        node_color=node_colors,
        ax=ax
    )
    
    # Draw node labels
    nx.draw_networkx_labels(graph, pos, font_size=10, ax=ax)
    
    # Draw edges
    if edge_color_map:
        for edge_type, color in edge_color_map.items():
            # Get edges of this type
            edges = [(u, v) for u, v, d in graph.edges(data=True) 
                     if d.get("relation_type") == edge_type]
            if edges:
                nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color=color, ax=ax)
    else:
        nx.draw_networkx_edges(graph, pos, ax=ax)
    
    # Draw edge labels
    edge_labels = {(u, v): d.get("relation_type", "") 
                   for u, v, d in graph.edges(data=True)}
    nx.draw_networkx_edge_labels(
        graph, pos, 
        edge_labels=edge_labels,
        font_size=8,
        ax=ax
    )
    
    # Set plot title and remove axis
    plt.title(title)
    plt.axis("off")
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    
    # Show or return
    if show:
        plt.show()
        return None
    else:
        return fig


def create_interactive_graph(
    graph: nx.DiGraph,
    title: str = "Interactive Knowledge Graph",
    height: str = "750px",
    width: str = "100%",
    bgcolor: str = "#ffffff",
    font_color: str = "#000000",
    node_color_map: Optional[Dict[str, str]] = None,
    save_path: Optional[Path] = None,
    show_buttons: bool = True,
    notebook: bool = False
) -> Optional[str]:
    """
    Create an interactive HTML visualization of the knowledge graph
    
    Args:
        graph: The NetworkX graph to visualize
        title: The title of the visualization
        height: The height of the visualization
        width: The width of the visualization
        bgcolor: The background color
        font_color: The font color
        node_color_map: Mapping from node types to colors
        save_path: Path to save the HTML file
        show_buttons: Whether to show the navigation buttons
        notebook: Whether to display in a Jupyter notebook
        
    Returns:
        The path to the HTML file if save_path is provided, otherwise None
    """
    if not HAS_PYVIS:
        logger.error("Pyvis is required for interactive visualization. Install with pip install pyvis")
        return None
    
    # Default color map if not provided
    if node_color_map is None:
        node_color_map = {
            "PERSON": "#6495ED",  # cornflowerblue
            "ORG": "#90EE90",     # lightgreen
            "GPE": "#FA8072",     # salmon
            "LOC": "#FFA500",     # orange
            "PRODUCT": "#800080", # purple
            "EVENT": "#FFFF00",   # yellow
            "WORK_OF_ART": "#FFC0CB", # pink
            "LAW": "#A52A2A",     # brown
            "LANGUAGE": "#808080", # gray
            "DATE": "#00FFFF",    # cyan
            "TIME": "#ADD8E6",    # lightblue
            "MONEY": "#008000",   # green
            "QUANTITY": "#FF0000", # red
            "PERCENT": "#0000FF", # blue
            "CARDINAL": "#FF00FF", # magenta
            "ORDINAL": "#008080"   # teal
        }
    
    # Create network
    net = Network(height=height, width=width, bgcolor=bgcolor, font_color=font_color, notebook=notebook)
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100,
                "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {
                "enabled": true,
                "iterations": 1000
            }
        },
        "interaction": {
            "navigationButtons": %s,
            "hover": true
        }
    }
    """ % ("true" if show_buttons else "false"))
    
    # Add nodes with attributes
    for node in graph.nodes():
        node_data = graph.nodes[node]
        entity_type = node_data.get("entity_type", "UNKNOWN")
        mentions = ", ".join(node_data.get("mentions", [node]))
        title = f"Type: {entity_type}<br>Mentions: {mentions}"
        color = node_color_map.get(entity_type, "#CCCCCC")
        
        net.add_node(
            node, 
            label=node, 
            title=title,
            color=color
        )
    
    # Add edges with attributes
    for source, target, data in graph.edges(data=True):
        relation_type = data.get("relation_type", "")
        sentence = data.get("sentence", "")
        title = f"{relation_type}<br><small>{sentence}</small>"
        
        net.add_edge(
            source, 
            target, 
            label=relation_type,
            title=title
        )
    
    # Save or show
    if save_path:
        net.save_graph(str(save_path))
        return str(save_path)
    else:
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "graph.html")
        net.save_graph(temp_path)
        return temp_path


def create_3d_graph(
    graph: nx.DiGraph,
    title: str = "3D Knowledge Graph",
    node_color_map: Optional[Dict[str, str]] = None,
    save_path: Optional[Path] = None,
    node_size: int = 10,
    edge_width: int = 2,
    notebook: bool = False
) -> Optional[str]:
    """
    Create an interactive 3D visualization of the knowledge graph using Plotly
    
    Args:
        graph: The NetworkX graph to visualize
        title: The title of the visualization
        node_color_map: Mapping from node types to colors
        save_path: Path to save the HTML file
        node_size: Size of the nodes in the visualization
        edge_width: Width of the edges in the visualization
        notebook: Whether to display in a Jupyter notebook
        
    Returns:
        The path to the HTML file if save_path is provided, otherwise None
    """
    if not HAS_PLOTLY:
        logger.error("Plotly is required for 3D visualization. Install with pip install plotly")
        return None
    
    # Default color map if not provided
    if node_color_map is None:
        node_color_map = {
            "PERSON": "#6495ED",  # cornflowerblue
            "ORG": "#90EE90",     # lightgreen
            "GPE": "#FA8072",     # salmon
            "LOC": "#FFA500",     # orange
            "PRODUCT": "#800080", # purple
            "EVENT": "#FFFF00",   # yellow
            "WORK_OF_ART": "#FFC0CB", # pink
            "LAW": "#A52A2A",     # brown
            "LANGUAGE": "#808080", # gray
            "DATE": "#00FFFF",    # cyan
            "TIME": "#ADD8E6",    # lightblue
            "MONEY": "#008000",   # green
            "QUANTITY": "#FF0000", # red
            "PERCENT": "#0000FF", # blue
            "CARDINAL": "#FF00FF", # magenta
            "ORDINAL": "#008080"   # teal
        }
    
    # Create 3D positions for nodes (using a force-directed algorithm in 3D)
    # For simplicity, we'll use a random initialization and a simple force-directed approach
    pos_3d = nx.spring_layout(graph, dim=3, seed=42)
    
    # Extract node positions
    node_x = []
    node_y = []
    node_z = []
    node_text = []
    node_colors = []
    
    for node in graph.nodes():
        x, y, z = pos_3d[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        
        # Node attributes
        node_data = graph.nodes[node]
        entity_type = node_data.get("entity_type", "UNKNOWN")
        mentions = ", ".join(node_data.get("mentions", [node]))
        node_text.append(f"{node}<br>Type: {entity_type}<br>Mentions: {mentions}")
        
        # Node color
        color = node_color_map.get(entity_type, "#CCCCCC")
        node_colors.append(color)
    
    # Create edges
    edge_x = []
    edge_y = []
    edge_z = []
    edge_text = []
    
    for source, target, data in graph.edges(data=True):
        x0, y0, z0 = pos_3d[source]
        x1, y1, z1 = pos_3d[target]
        
        # Create line for the edge
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])
        
        # Edge attributes
        relation_type = data.get("relation_type", "")
        sentence = data.get("sentence", "")
        edge_text.append(f"{source} → {target}<br>{relation_type}<br>{sentence}")
    
    # Create node trace
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color=node_colors,
            line=dict(width=1, color='#888'),
            opacity=0.8
        ),
        text=node_text,
        hoverinfo='text'
    )
    
    # Create edge trace
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(width=edge_width, color='#888'),
        hoverinfo='text',
        text=edge_text * (len(edge_x) // 3)  # Repeat for each edge segment
    )
    
    # Create figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            showlegend=False,
            margin=dict(b=0, l=0, r=0, t=40),
            hovermode='closest',
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
    )
    
    # Save or show
    if save_path:
        pio.write_html(fig, file=str(save_path), auto_open=False)
        return str(save_path)
    elif notebook:
        # For Jupyter notebooks
        return fig
    else:
        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "3d_graph.html")
        pio.write_html(fig, file=temp_path, auto_open=True)
        return temp_path


def export_graph_to_formats(
    graph: nx.DiGraph,
    base_path: Path,
    formats: List[str] = ["json", "gexf", "graphml"]
) -> Dict[str, Path]:
    """
    Export a knowledge graph to multiple formats
    
    Args:
        graph: The NetworkX graph to export
        base_path: The base path to save the files (without extension)
        formats: List of formats to export (json, gexf, graphml, etc.)
        
    Returns:
        Dictionary mapping formats to file paths
    """
    result = {}
    base_path = Path(base_path)
    
    for fmt in formats:
        if fmt.lower() == "json":
            # Custom JSON export
            data = {
                "nodes": [
                    {
                        "id": node,
                        "label": node,
                        **graph.nodes[node]
                    }
                    for node in graph.nodes()
                ],
                "edges": [
                    {
                        "source": source,
                        "target": target,
                        "type": data.get("relation_type", ""),
                        **data
                    }
                    for source, target, data in graph.edges(data=True)
                ]
            }
            
            path = base_path.with_suffix(".json")
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            
            result["json"] = path
        
        elif fmt.lower() == "gexf":
            path = base_path.with_suffix(".gexf")
            nx.write_gexf(graph, path)
            result["gexf"] = path
        
        elif fmt.lower() == "graphml":
            path = base_path.with_suffix(".graphml")
            nx.write_graphml(graph, path)
            result["graphml"] = path
        
        elif fmt.lower() == "cytoscape":
            # Export for Cytoscape (specialized JSON format)
            data = {
                "elements": {
                    "nodes": [
                        {
                            "data": {
                                "id": node,
                                "label": node,
                                **graph.nodes[node]
                            }
                        }
                        for node in graph.nodes()
                    ],
                    "edges": [
                        {
                            "data": {
                                "id": f"{source}-{target}",
                                "source": source,
                                "target": target,
                                "label": data.get("relation_type", ""),
                                **data
                            }
                        }
                        for source, target, data in graph.edges(data=True)
                    ]
                }
            }
            
            path = base_path.with_suffix(".cyjs")
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            
            result["cytoscape"] = path
            
        else:
            logger.warning(f"Unsupported export format: {fmt}")
    
    return result


def create_knowledge_map(
    graph: nx.DiGraph,
    title: str = "Knowledge Map",
    node_color_map: Optional[Dict[str, str]] = None,
    save_path: Optional[Path] = None,
    notebook: bool = False
) -> Optional[str]:
    """
    Create a hierarchical tree-map visualization of the knowledge graph
    
    Args:
        graph: The NetworkX graph to visualize
        title: The title of the visualization
        node_color_map: Mapping from node types to colors
        save_path: Path to save the HTML file
        notebook: Whether to display in a Jupyter notebook
        
    Returns:
        The path to the HTML file if save_path is provided, otherwise None
    """
    if not HAS_PLOTLY:
        logger.error("Plotly is required for knowledge map visualization. Install with pip install plotly")
        return None
    
    # Default color map if not provided
    if node_color_map is None:
        node_color_map = {
            "PERSON": "#6495ED",  # cornflowerblue
            "ORG": "#90EE90",     # lightgreen
            "GPE": "#FA8072",     # salmon
            "LOC": "#FFA500",     # orange
            "PRODUCT": "#800080", # purple
            "EVENT": "#FFFF00",   # yellow
            "WORK_OF_ART": "#FFC0CB", # pink
            "LAW": "#A52A2A",     # brown
            "LANGUAGE": "#808080", # gray
            "DATE": "#00FFFF",    # cyan
            "TIME": "#ADD8E6",    # lightblue
            "MONEY": "#008000",   # green
            "QUANTITY": "#FF0000", # red
            "PERCENT": "#0000FF", # blue
            "CARDINAL": "#FF00FF", # magenta
            "ORDINAL": "#008080"   # teal
        }
    
    # Group entities by type
    entity_types = {}
    for node, data in graph.nodes(data=True):
        entity_type = data.get("entity_type", "UNKNOWN")
        if entity_type not in entity_types:
            entity_types[entity_type] = []
        entity_types[entity_type].append(node)
    
    # Create a hierarchical structure for the treemap
    treemap_data = []
    
    # First level: Entity types
    for entity_type, entities in entity_types.items():
        color = node_color_map.get(entity_type, "#CCCCCC")
        
        # Second level: Entities of this type
        children = []
        for entity in entities:
            # Get connections count for sizing
            connections = len(list(graph.successors(entity))) + len(list(graph.predecessors(entity)))
            
            # Add entity to children
            children.append({
                "name": entity,
                "value": max(1, connections),  # Ensure non-zero size
                "color": color
            })
        
        # Add entity type to treemap
        treemap_data.append({
            "name": entity_type,
            "children": children,
            "color": color
        })
    
    # Create a sunburst chart (hierarchical visualization)
    labels = []
    parents = []
    values = []
    colors = []
    
    # Add root node
    labels.append("All Entities")
    parents.append("")
    values.append(0)  # Size doesn't matter for root
    colors.append("#FFFFFF")  # White or transparent
    
    # Add entity types
    for entity_type_data in treemap_data:
        entity_type = entity_type_data["name"]
        labels.append(entity_type)
        parents.append("All Entities")
        # Sum of all child values
        type_value = sum(child["value"] for child in entity_type_data["children"])
        values.append(type_value)
        colors.append(entity_type_data["color"])
        
        # Add entities
        for entity_data in entity_type_data["children"]:
            labels.append(entity_data["name"])
            parents.append(entity_type)
            values.append(entity_data["value"])
            colors.append(entity_data["color"])
    
    # Create figure
    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors
            ),
            hovertemplate="<b>%{label}</b><br>Connections: %{value}<extra></extra>",
        )
    )
    
    fig.update_layout(
        title=title,
        margin=dict(t=30, l=0, r=0, b=0)
    )
    
    # Save or show
    if save_path:
        pio.write_html(fig, file=str(save_path), auto_open=False)
        return str(save_path)
    elif notebook:
        # For Jupyter notebooks
        return fig
    else:
        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "knowledge_map.html")
        pio.write_html(fig, file=temp_path, auto_open=True)
        return temp_path 