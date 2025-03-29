"""
MLX utilities for LlamaGraph
"""
import logging
from typing import List, Dict, Any, Union, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Check if MLX is available
try:
    import mlx.core as mx
    HAS_MLX = True
except ImportError:
    HAS_MLX = False
    logger.warning("MLX not available. Some optimizations will be disabled.")

class MLXProcessor:
    """Wrapper for MLX operations with fallback to NumPy"""
    def __init__(self, use_mlx: bool = True):
        self.use_mlx = use_mlx and HAS_MLX
        logger.info(f"MLX acceleration: {'Enabled' if self.use_mlx else 'Disabled'}")
    
    def array(self, data: Union[List, np.ndarray]) -> Union[Any, np.ndarray]:
        """Create an array using MLX or NumPy"""
        if self.use_mlx:
            return mx.array(data)
        else:
            return np.array(data)
    
    def matmul(self, a: Any, b: Any) -> Any:
        """Matrix multiplication using MLX or NumPy"""
        if self.use_mlx:
            return mx.matmul(a, b)
        else:
            return np.matmul(a, b)
    
    def argmax(self, x: Any, axis: int = 0) -> Any:
        """Argmax using MLX or NumPy"""
        if self.use_mlx:
            return mx.argmax(x, axis=axis)
        else:
            return np.argmax(x, axis=axis)
    
    def softmax(self, x: Any, axis: int = -1) -> Any:
        """Softmax using MLX or NumPy"""
        if self.use_mlx:
            return mx.softmax(x, axis=axis)
        else:
            # NumPy implementation of softmax
            e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
            return e_x / e_x.sum(axis=axis, keepdims=True)
    
    def to_numpy(self, x: Any) -> np.ndarray:
        """Convert to NumPy array"""
        if self.use_mlx:
            return mx.to_numpy(x)
        else:
            return x
    
    def vectorize(self, func: callable) -> callable:
        """Vectorize a function using MLX or NumPy"""
        if self.use_mlx:
            # MLX doesn't have a direct vectorize equivalent, so this is a simplified version
            # that uses mx.vmap for the most basic case
            try:
                return mx.vmap(func)
            except Exception as e:
                logger.warning(f"MLX vectorization failed: {e}. Falling back to NumPy.")
                return np.vectorize(func)
        else:
            return np.vectorize(func) 