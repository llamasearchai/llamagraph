"""
Caching module for LlamaGraph
"""
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict

logger = logging.getLogger(__name__)

class Cache:
    """LRU cache implementation for LlamaGraph"""
    def __init__(self, cache_dir: Path, max_size: int = 100):
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.cache = OrderedDict()
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load cached data if available
        self._load_cache()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache"""
        if key in self.cache:
            # Move the item to the end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        
        # Try to load from disk
        cache_file = self._get_cache_file(key)
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    value = json.load(f)
                
                # Add to in-memory cache
                self.cache[key] = value
                
                # Ensure cache doesn't exceed max size
                self._prune_cache()
                
                return value
            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_file}: {e}")
        
        return None
    
    def set(self, key: str, value: Any):
        """Set a value in the cache"""
        # Add to in-memory cache
        self.cache[key] = value
        
        # Ensure cache doesn't exceed max size
        self._prune_cache()
        
        # Save to disk
        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, "w") as f:
                json.dump(value, f)
        except Exception as e:
            logger.warning(f"Failed to save cache file {cache_file}: {e}")
    
    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        
        # Remove cache files
        for file in self.cache_dir.glob("*.cache"):
            try:
                file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete cache file {file}: {e}")
    
    def _prune_cache(self):
        """Prune the cache to ensure it doesn't exceed max size"""
        while len(self.cache) > self.max_size:
            # Remove oldest item (first in OrderedDict)
            key, _ = self.cache.popitem(last=False)
            
            # Remove from disk as well
            cache_file = self._get_cache_file(key)
            try:
                if cache_file.exists():
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")
    
    def _get_cache_file(self, key: str) -> Path:
        """Get the cache file path for a key"""
        # Use a hash of the key as the filename to avoid invalid characters
        filename = f"{abs(hash(key))}.cache"
        return self.cache_dir / filename
    
    def _load_cache(self):
        """Load cache from disk"""
        # Load the most recent cache files, up to max_size
        cache_files = list(self.cache_dir.glob("*.cache"))
        cache_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        for file in cache_files[:self.max_size]:
            try:
                key = file.stem  # Use filename as key
                with open(file, "r") as f:
                    value = json.load(f)
                self.cache[key] = value
            except Exception as e:
                logger.warning(f"Failed to load cache file {file}: {e}") 