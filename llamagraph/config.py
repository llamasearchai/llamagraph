"""
Configuration for LlamaGraph
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class LlamaGraphConfig:
    """Configuration for LlamaGraph"""
    # Extraction settings
    entity_types: List[str] = None  # Types of entities to extract
    relation_patterns: Dict[str, str] = None  # Patterns for relation extraction
    
    # Performance settings
    use_mlx: bool = True  # Use MLX for acceleration
    num_threads: int = os.cpu_count()  # Number of threads for processing
    
    # UI settings
    animation_speed: float = 0.05  # Speed of animations
    theme: str = "rainbow"  # Color theme
    
    # Cache settings
    cache_dir: Path = Path.home() / ".llamagraph" / "cache"
    max_cache_size: int = 100  # Maximum number of cached results
    
    # File paths
    output_dir: Path = Path.home() / ".llamagraph" / "outputs"
    
    def __post_init__(self):
        """Initialize default values and create directories"""
        if self.entity_types is None:
            self.entity_types = [
                "PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT",
                "WORK_OF_ART", "LAW", "LANGUAGE", "DATE", "TIME",
                "MONEY", "QUANTITY", "PERCENT", "CARDINAL", "ORDINAL"
            ]
        
        if self.relation_patterns is None:
            self.relation_patterns = {
                "works_for": r"(\w+) (work|works|worked) for (\w+)",
                "founded": r"(\w+) (found|founds|founded) (\w+)",
                "created": r"(\w+) (create|creates|created) (\w+)",
                "located_in": r"(\w+) (is|are|was|were) (located|based) in (\w+)",
                "has_role": r"(\w+) (is|are|was|were) (\w+)'s (\w+)",
                "born_in": r"(\w+) (was|were) born in (\w+)",
            }
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

# Create default configuration
DEFAULT_CONFIG = LlamaGraphConfig() 