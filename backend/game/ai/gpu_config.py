"""
GPU configuration utilities for TensorFlow on Mac.
"""

import tensorflow as tf
import logging

logger = logging.getLogger(__name__)


def check_gpu_availability():
    """
    Check if GPU is available for TensorFlow.
    
    Returns:
        bool: True if GPU is available, False otherwise
    """
    try:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logger.info(f"GPU devices found: {len(gpus)}")
            for gpu in gpus:
                logger.info(f"  - {gpu.name}")
            return True
        else:
            logger.info("No GPU devices found. Using CPU.")
            return False
    except Exception as e:
        logger.warning(f"Error checking GPU availability: {e}")
        return False


def configure_gpu():
    """
    Configure TensorFlow to use GPU if available.
    Sets up memory growth to avoid allocating all GPU memory at once.
    """
    try:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            # Enable memory growth to avoid allocating all GPU memory
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logger.info("GPU configured with memory growth enabled")
            return True
        else:
            logger.info("No GPU available, using CPU")
            return False
    except Exception as e:
        logger.warning(f"Error configuring GPU: {e}")
        return False


def get_device_info():
    """
    Get information about available compute devices.
    
    Returns:
        dict: Information about available devices
    """
    info = {
        'gpu_available': False,
        'gpu_count': 0,
        'gpu_devices': [],
        'cpu_available': True,
    }
    
    try:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            info['gpu_available'] = True
            info['gpu_count'] = len(gpus)
            info['gpu_devices'] = [gpu.name for gpu in gpus]
        
        cpus = tf.config.list_physical_devices('CPU')
        info['cpu_count'] = len(cpus) if cpus else 1
        
    except Exception as e:
        logger.warning(f"Error getting device info: {e}")
    
    return info

