"""
Threading utilities for LlamaGraph
"""
import time
import logging
from typing import List, Callable, Any, TypeVar, Generic
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')

def parallel_process(
    items: List[T],
    process_func: Callable[[T], R],
    num_threads: int = 4,
    description: str = "Processing",
    show_progress: bool = True
) -> List[R]:
    """
    Process items in parallel using multiple threads
    
    Args:
        items: List of items to process
        process_func: Function to apply to each item
        num_threads: Number of threads to use
        description: Description for the progress bar
        show_progress: Whether to show a progress bar
    
    Returns:
        List of results, one for each input item
    """
    results = [None] * len(items)
    
    # Create thread pool
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(process_func, item): i 
            for i, item in enumerate(items)
        }
        
        # Process results as they complete
        if show_progress:
            for future in tqdm(
                as_completed(future_to_index), 
                total=len(items),
                desc=description
            ):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Error processing item {index}: {e}")
                    results[index] = None
        else:
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Error processing item {index}: {e}")
                    results[index] = None
    
    return results 