"""
Terminal UI for LlamaGraph
"""
import sys
import time
import random
import json
from typing import List, Dict, Any, Optional, Union

import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.tree import Tree
from rich.box import ROUNDED

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import ANSI

from llamagraph.graph.knowledge_graph import KnowledgeGraph
from llamagraph.graph.query_engine import QueryEngine
from llamagraph.ui.colors import COLOR_SCHEME, THEMES
from llamagraph.ui.animations import (
    animate_typing,
    animate_llama,
    spinner_task,
    progress_bar,
    loading_animation,
)

console = Console()

class LlamaGraphTerminal:
    """Terminal UI for LlamaGraph"""
    def __init__(self, theme: str = "llama"):
        self.theme = theme
        self.colors = COLOR_SCHEME.get(theme, COLOR_SCHEME["llama"])
        self.styles = THEMES.get(theme, THEMES["llama"])
        
        # Set up prompt with auto-completion
        self.command_completer = WordCompleter([
            "find", "path from", "related", "count entities", 
            "count relations", "export", "help", "exit"
        ])
        
        self.prompt_style = Style.from_dict({
            "prompt": f"ansi{self._ansi_color(self.colors['primary'])}",
        })
        
        self.prompt_session = PromptSession(
            history=InMemoryHistory(),
            completer=self.command_completer,
            style=self.prompt_style,
            complete_while_typing=True
        )
    
    def display_welcome(self):
        """Display welcome banner"""
        # Clear screen
        console.clear()
        
        # Generate llama ASCII art title with pyfiglet
        title = pyfiglet.figlet_format("LlamaGraph", font="standard")
        
        # Create welcome panel
        welcome_panel = Panel(
            f"[{self.colors['primary']}]{title}[/]\n"
            f"[{self.colors['secondary']}]🦙 A llama-themed knowledge graph construction tool[/]\n"
            f"[{self.colors['info']}]Version 1.0.0[/]",
            title="Welcome to LlamaGraph",
            border_style=self.colors["accent"],
            padding=(1, 2)
        )
        
        console.print(welcome_panel)
        console.print("")
        
        # Animate a simple ASCII llama
        animate_llama(frames=5, speed=0.2)
    
    def animate_typing(self, text: str):
        """Animate typing text"""
        animate_typing(text, color=self.colors["secondary"])
    
    def animate_processing(self, message: str):
        """Show a loading animation with a message"""
        loading_animation(
            f"[{self.colors['info']}]{message}[/]", 
            duration=1.0,
            spinner_type="dots"
        )
    
    def display_success(self, message: str):
        """Display a success message"""
        console.print(f"🦙 [{self.colors['success']}]{message}[/]")
    
    def display_error(self, message: str):
        """Display an error message"""
        console.print(f"🦙 [{self.colors['error']}]{message}[/]")
    
    def display_warning(self, message: str):
        """Display a warning message"""
        console.print(f"🦙 [{self.colors['warning']}]{message}[/]")
    
    def display_info(self, message: str):
        """Display an info message"""
        console.print(f"🦙 [{self.colors['info']}]{message}[/]")
    
    def display_entity(self, entity: Dict[str, Any]):
        """Display entity information"""
        panel = Panel(
            f"[bold]Type:[/] [{self.styles['entity']}]{entity['entity_type']}[/]\n"
            f"[bold]Occurrences:[/] {entity['occurrences']}\n"
            f"[bold]Mentions:[/] {', '.join(entity['mentions'])}",
            title=f"[{self.styles['heading']}]Entity: {entity['text']}[/]",
            border_style=self.colors["primary"],
            padding=(1, 2)
        )
        console.print(panel)
    
    def display_relations(self, relations: List[Dict[str, Any]]):
        """Display relations for an entity"""
        if not relations:
            self.display_info("No relations found for this entity.")
            return
        
        # Create a table for outgoing relations
        outgoing = [r for r in relations if r["direction"] == "outgoing"]
        if outgoing:
            out_table = Table(
                title="Outgoing Relations",
                box=ROUNDED,
                border_style=self.colors["secondary"]
            )
            out_table.add_column("Relation", style=self.styles["relation"])
            out_table.add_column("Target Entity", style=self.styles["entity"])
            
            for rel in outgoing:
                out_table.add_row(
                    rel["relation_type"],
                    rel["entity"]
                )
            
            console.print(out_table)
        
        # Create a table for incoming relations
        incoming = [r for r in relations if r["direction"] == "incoming"]
        if incoming:
            in_table = Table(
                title="Incoming Relations",
                box=ROUNDED,
                border_style=self.colors["secondary"]
            )
            in_table.add_column("Source Entity", style=self.styles["entity"])
            in_table.add_column("Relation", style=self.styles["relation"])
            
            for rel in incoming:
                in_table.add_row(
                    rel["entity"],
                    rel["relation_type"]
                )
            
            console.print(in_table)
    
    def display_path(self, path: List[Dict[str, Any]]):
        """Display a path between entities"""
        if not path:
            self.display_info("No path found between these entities.")
            return
        
        # Create a visualization of the path
        tree = Tree(f"[{self.styles['heading']}]Path:[/]")
        
        for i, step in enumerate(path):
            source = step["source"]
            relation = step["relation_type"]
            target = step["target"]
            
            if i == 0:
                branch = tree.add(f"[{self.styles['entity']}]{source}[/]")
            else:
                branch = branch.add(f"[{self.styles['entity']}]{source}[/]")
                
            branch = branch.add(f"[{self.styles['relation']}]{relation}[/]")
            
            if i == len(path) - 1:
                branch.add(f"[{self.styles['entity']}]{target}[/]")
        
        console.print(tree)
    
    def display_graph_summary(self, graph: KnowledgeGraph):
        """Display a summary of the knowledge graph"""
        summary = graph.get_summary()
        
        # Create a panel with the summary
        panel = Panel(
            f"[bold]Entities:[/] {summary['num_entities']}\n"
            f"[bold]Relations:[/] {summary['num_relations']}\n\n"
            f"[{self.styles['heading']}]Entity Types:[/]\n" +
            "\n".join([f"- {k}: {v}" for k, v in summary['entity_types'].items()]) +
            f"\n\n[{self.styles['heading']}]Relation Types:[/]\n" +
            "\n".join([f"- {k}: {v}" for k, v in summary['relation_types'].items()]) +
            f"\n\n[{self.styles['heading']}]Most Connected Entities:[/]\n" +
            "\n".join([f"- {e['entity']} ({e['type']}): {e['connections']} connections" 
                      for e in summary['most_connected']]),
            title="Knowledge Graph Summary",
            border_style=self.colors["accent"],
            padding=(1, 2)
        )
        
        console.print(panel)
    
    def display_json(self, json_data: Any):
        """Display JSON data"""
        json_str = json.dumps(json_data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        
        console.print(syntax)
    
    def display_help(self, commands: List[Dict[str, str]]):
        """Display help information"""
        table = Table(
            title="Available Commands",
            box=ROUNDED,
            border_style=self.colors["info"]
        )
        table.add_column("Command", style=self.styles["command"])
        table.add_column("Description", style=self.styles["text"])
        
        for cmd in commands:
            table.add_row(cmd["command"], cmd["description"])
        
        console.print(table)
    
    def run_interactive_mode(self, graph: KnowledgeGraph):
        """Run interactive query mode"""
        query_engine = QueryEngine(graph)
        
        self.display_info("Knowledge graph is ready for querying!")
        self.display_info("Type 'help' for available commands or 'exit' to quit.")
        
        while True:
            try:
                # Get command from user with auto-completion
                prompt_text = ANSI(f"\n[{self._ansi_color(self.colors['primary'])}]🦙 > [/{self._ansi_color(self.colors['primary'])}]")
                command = self.prompt_session.prompt(prompt_text)
                
                if not command:
                    continue
                
                if command.lower() == "exit" or command.lower() == "quit":
                    self.animate_typing("Goodbye! The llama waves farewell.")
                    break
                
                # Execute the query
                result = query_engine.execute_query(command)
                
                if result["success"]:
                    console.print(f"[{self.colors['success']}]{result['message']}[/]")
                    
                    # Display query-specific results
                    data = result["data"]
                    if data:
                        if "entity" in data and "relations" in data:
                            # Display entity and its relations
                            self.display_entity(data["entity"])
                            self.display_relations(data["relations"])
                        
                        elif "path" in data:
                            # Display path between entities
                            self.display_path(data["path"])
                        
                        elif "counts" in data:
                            # Display counts
                            table = Table(
                                title=f"Count Results (Total: {data['total']})",
                                box=ROUNDED,
                                border_style=self.colors["info"]
                            )
                            table.add_column("Type")
                            table.add_column("Count")
                            
                            for k, v in data["counts"].items():
                                table.add_row(k, str(v))
                            
                            console.print(table)
                        
                        elif "commands" in data:
                            # Display help commands
                            self.display_help(data["commands"])
                        
                        elif "direct_relations" in data and "similar_entities" in data:
                            # Display related entities
                            if data["similar_entities"]:
                                table = Table(
                                    title="Similar Entities",
                                    box=ROUNDED,
                                    border_style=self.colors["secondary"]
                                )
                                table.add_column("Entity", style=self.styles["entity"])
                                table.add_column("Shared Relation", style=self.styles["relation"])
                                table.add_column("Via", style=self.styles["text"])
                                
                                for item in data["similar_entities"]:
                                    table.add_row(
                                        item["entity"],
                                        item["shared_relation_type"],
                                        item["via"]
                                    )
                                
                                console.print(table)
                            else:
                                self.display_info("No similar entities found.")
                else:
                    self.display_error(result["message"])
            
            except KeyboardInterrupt:
                self.display_warning("Operation cancelled.")
            except Exception as e:
                self.display_error(f"Error: {str(e)}")
    
    def _ansi_color(self, color_name: str) -> str:
        """Convert rich color to ANSI color code for prompt_toolkit"""
        # Simple mapping for common colors
        color_map = {
            "bright_cyan": "96",
            "bright_green": "92",
            "bright_yellow": "93",
            "bright_magenta": "95",
            "bright_blue": "94",
            "bright_red": "91",
            "cyan": "36",
            "green": "32",
            "yellow": "33",
            "magenta": "35",
            "blue": "34",
            "red": "31",
        }
        
        return color_map.get(color_name, "37")  # Default to white 