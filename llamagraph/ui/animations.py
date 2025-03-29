"""
Terminal animations for LlamaGraph
"""
import time
import sys
import random
from typing import List, Optional, Callable
import threading

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, TextColumn, BarColumn, SpinnerColumn

from llamagraph.ui.colors import COLORS

console = Console()

def animate_typing(text: str, delay: float = 0.03, color: str = "yellow"):
    """Animate typing text character by character"""
    for char in text:
        console.print(char, end="", style=color)
        time.sleep(delay)
    console.print("")

def animate_llama(frames: int = 20, speed: float = 0.1):
    """Animate a simple ASCII llama"""
    llama_frames = [
        r"""
         \   ^__^
          \  (oo)\_______
             (__)\       )\/\
                 ||----w |
                 ||     ||
        """,
        r"""
         \   ^__^
          \  (oo)\_______
             (__)\       )\/\
                 ||----w |
                |  ||     ||
        """,
        r"""
         \   ^__^
          \  (oo)\_______
             (__)\       )\/\
                |  ||----w |
                 ||     ||
        """
    ]
    
    for _ in range(frames):
        frame = random.choice(llama_frames)
        console.clear()
        console.print(frame, style=random.choice(COLORS))
        time.sleep(speed)

def spinner_task(message: str, task: Callable, *args, **kwargs):
    """Run a task with a spinner animation"""
    result = [None]
    error = [None]
    
    def worker():
        try:
            result[0] = task(*args, **kwargs)
        except Exception as e:
            error[0] = e
    
    thread = threading.Thread(target=worker)
    thread.start()
    
    with console.status(message, spinner="dots") as status:
        while thread.is_alive():
            time.sleep(0.1)
    
    thread.join()
    
    if error[0]:
        raise error[0]
    
    return result[0]

def progress_bar(items: List, description: str = "Processing", total: Optional[int] = None):
    """Create a rich progress bar"""
    total = total or len(items)
    
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
    )
    
    task_id = progress.add_task(description, total=total)
    
    return progress, task_id

def loading_animation(message: str, duration: float = 2.0, spinner_type: str = "dots"):
    """Show a loading animation for a specified duration"""
    with console.status(message, spinner=spinner_type) as status:
        time.sleep(duration) 