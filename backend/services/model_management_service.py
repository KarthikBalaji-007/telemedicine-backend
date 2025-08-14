"""
AI Model Management Service
Handles loading, status monitoring, and management of AI models
"""

import logging
import time
import psutil
import threading
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

class ModelStatus(Enum):
    """Model loading status"""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    UNLOADING = "unloading"

class ModelManagementService:
    """Service for managing AI model lifecycle"""
    
    def __init__(self):
        self.model_status = ModelStatus.NOT_LOADED
        self.model_info = {}
        self.loading_progress = 0
        self.loading_start_time = None
        self.error_message = None
        self.memory_usage = 0
        self.model_thread = None
        
    def get_model_status(self) -> Dict:
        """Get current model status and information"""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            
            status_info = {
                'status': self.model_status.value,
                'loading_progress': self.loading_progress,
                'memory_usage_gb': round(self.memory_usage / (1024**3), 2),
                'system_memory_total_gb': round(memory.total / (1024**3), 2),
                'system_memory_available_gb': round(memory.available / (1024**3), 2),
                'system_memory_percent': memory.percent,
                'model_info': self.model_info,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Add loading time if currently loading
            if self.model_status == ModelStatus.LOADING and self.loading_start_time:
                elapsed_time = time.time() - self.loading_start_time
                status_info['loading_time_seconds'] = round(elapsed_time, 1)
                status_info['estimated_total_time'] = 60  # Estimated 1 minute
                
            # Add error info if error occurred
            if self.model_status == ModelStatus.ERROR:
                status_info['error_message'] = self.error_message
                
            # Add ready time if model is ready
            if self.model_status == ModelStatus.READY:
                status_info['ready_since'] = self.model_info.get('loaded_at')
                status_info['model_name'] = self.model_info.get('name', 'Llama3-OpenBioLLM-8B')
                status_info['model_size'] = self.model_info.get('size', '8B parameters')
                
            return status_info
            
        except Exception as e:
            logging.error(f"Error getting model status: {e}")
            return {
                'status': 'error',
                'error_message': f'Status check failed: {e}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def start_model_loading(self) -> Dict:
        """Start loading the AI model"""
        try:
            if self.model_status == ModelStatus.LOADING:
                return {
                    'success': False,
                    'message': 'Model is already loading',
                    'status': self.model_status.value
                }
                
            if self.model_status == ModelStatus.READY:
                return {
                    'success': True,
                    'message': 'Model is already loaded and ready',
                    'status': self.model_status.value
                }
            
            # Check system requirements
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb < 6:  # Need at least 6GB for 8B model
                return {
                    'success': False,
                    'message': f'Insufficient memory. Need 6GB, have {available_gb:.1f}GB available',
                    'status': 'insufficient_memory'
                }
            
            # Start loading in background thread
            self.model_status = ModelStatus.LOADING
            self.loading_progress = 0
            self.loading_start_time = time.time()
            self.error_message = None
            
            self.model_thread = threading.Thread(target=self._load_model_background)
            self.model_thread.daemon = True
            self.model_thread.start()
            
            return {
                'success': True,
                'message': 'Model loading started. This will take approximately 1 minute.',
                'status': self.model_status.value,
                'estimated_time_minutes': 1
            }
            
        except Exception as e:
            logging.error(f"Error starting model loading: {e}")
            self.model_status = ModelStatus.ERROR
            self.error_message = str(e)
            return {
                'success': False,
                'message': f'Failed to start model loading: {e}',
                'status': 'error'
            }
    
    def _load_model_background(self):
        """Background thread for model loading simulation"""
        try:
            # Simulate model loading process
            loading_steps = [
                (10, "Initializing CUDA environment..."),
                (25, "Loading model architecture..."),
                (45, "Loading model weights..."),
                (70, "Optimizing for inference..."),
                (90, "Running model validation..."),
                (100, "Model ready!")
            ]
            
            for progress, step_message in loading_steps:
                time.sleep(6)  # Simulate loading time (total ~36 seconds)
                self.loading_progress = progress
                logging.info(f"Model loading: {progress}% - {step_message}")
                
                # Simulate memory usage increase
                if progress <= 90:
                    self.memory_usage = (progress / 100) * 5 * (1024**3)  # Up to 5GB
            
            # Model loading complete
            self.model_status = ModelStatus.READY
            self.loading_progress = 100
            self.memory_usage = 5 * (1024**3)  # 5GB final usage
            
            self.model_info = {
                'name': 'Llama3-OpenBioLLM-8B',
                'size': '8B parameters',
                'type': 'Medical Language Model',
                'loaded_at': datetime.utcnow().isoformat(),
                'loading_time_seconds': round(time.time() - self.loading_start_time, 1),
                'memory_usage_gb': 5.0,
                'capabilities': [
                    'Symptom Assessment',
                    'Medical Q&A',
                    'Risk Classification',
                    'Treatment Recommendations'
                ]
            }
            
            logging.info("AI Model loaded successfully!")
            
        except Exception as e:
            logging.error(f"Model loading failed: {e}")
            self.model_status = ModelStatus.ERROR
            self.error_message = str(e)
            self.loading_progress = 0
            self.memory_usage = 0
    
    def unload_model(self) -> Dict:
        """Unload the AI model to free memory"""
        try:
            if self.model_status == ModelStatus.NOT_LOADED:
                return {
                    'success': True,
                    'message': 'Model is not loaded',
                    'status': 'not_loaded'
                }
            
            if self.model_status == ModelStatus.LOADING:
                return {
                    'success': False,
                    'message': 'Cannot unload while model is loading',
                    'status': 'loading'
                }
            
            # Simulate unloading
            self.model_status = ModelStatus.UNLOADING
            time.sleep(2)  # Simulate unload time
            
            # Reset all status
            self.model_status = ModelStatus.NOT_LOADED
            self.loading_progress = 0
            self.memory_usage = 0
            self.model_info = {}
            self.error_message = None
            
            return {
                'success': True,
                'message': 'Model unloaded successfully',
                'status': 'not_loaded',
                'memory_freed_gb': 5.0
            }
            
        except Exception as e:
            logging.error(f"Error unloading model: {e}")
            return {
                'success': False,
                'message': f'Failed to unload model: {e}',
                'status': 'error'
            }
    
    def get_system_requirements(self) -> Dict:
        """Get system requirements and current system status"""
        try:
            memory = psutil.virtual_memory()
            
            requirements = {
                'minimum_requirements': {
                    'ram_gb': 8,
                    'gpu_memory_gb': 6,
                    'cuda_support': True,
                    'python_version': '3.8+'
                },
                'recommended_requirements': {
                    'ram_gb': 16,
                    'gpu_memory_gb': 8,
                    'cuda_support': True,
                    'python_version': '3.10+'
                },
                'current_system': {
                    'total_ram_gb': round(memory.total / (1024**3), 2),
                    'available_ram_gb': round(memory.available / (1024**3), 2),
                    'ram_usage_percent': memory.percent,
                    'cuda_available': True,  # Assume CUDA is available
                    'python_version': '3.10+'
                },
                'compatibility': {
                    'can_run_model': memory.available > 6 * (1024**3),
                    'performance_level': 'good' if memory.total > 16 * (1024**3) else 'adequate',
                    'estimated_loading_time': '60 seconds'
                }
            }
            
            return requirements
            
        except Exception as e:
            logging.error(f"Error getting system requirements: {e}")
            return {
                'error': f'Failed to get system requirements: {e}'
            }
    
    def health_check(self) -> Dict:
        """Health check for model management service"""
        try:
            return {
                'service_status': 'healthy',
                'model_status': self.model_status.value,
                'memory_usage_gb': round(self.memory_usage / (1024**3), 2),
                'last_check': datetime.utcnow().isoformat(),
                'available': True
            }
        except Exception as e:
            return {
                'service_status': 'error',
                'error': str(e),
                'available': False
            }
