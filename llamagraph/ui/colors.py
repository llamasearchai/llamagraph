"""
Color definitions for LlamaGraph
"""

# Basic color palette
COLORS = [
    "bright_cyan",
    "bright_green",
    "bright_yellow",
    "bright_magenta",
    "bright_blue",
    "bright_red",
    "cyan",
    "green",
    "yellow",
    "magenta",
    "blue",
]

# Color schemes
COLOR_SCHEME = {
    "llama": {
        "primary": "bright_cyan",
        "secondary": "bright_magenta",
        "accent": "bright_yellow",
        "success": "bright_green",
        "error": "bright_red",
        "warning": "yellow",
        "info": "bright_blue",
    },
    "forest": {
        "primary": "green",
        "secondary": "blue",
        "accent": "yellow",
        "success": "bright_green",
        "error": "red",
        "warning": "yellow",
        "info": "blue",
    },
    "rainbow": {
        "primary": "bright_magenta",
        "secondary": "bright_cyan",
        "accent": "bright_yellow",
        "success": "bright_green",
        "error": "bright_red",
        "warning": "yellow",
        "info": "bright_blue",
    }
}

# Theme-specific styles
THEMES = {
    "llama": {
        "entity": "bold bright_cyan",
        "relation": "italic bright_yellow",
        "command": "bold bright_magenta",
        "highlight": "reverse bright_white",
        "heading": "bold bright_cyan underline",
        "text": "white",
    },
    "forest": {
        "entity": "bold green",
        "relation": "italic yellow",
        "command": "bold blue",
        "highlight": "reverse white",
        "heading": "bold green underline",
        "text": "white",
    },
    "rainbow": {
        "entity": "bold bright_blue",
        "relation": "italic bright_yellow",
        "command": "bold bright_magenta",
        "highlight": "reverse bright_white",
        "heading": "bold bright_magenta underline",
        "text": "white",
    }
} 