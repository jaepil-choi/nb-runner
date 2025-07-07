"""
Configuration Manager for nb-runner

Handles environment variables, API keys, and configuration validation.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

class ConfigManager:
    """
    Centralized configuration manager for nb-runner system.
    
    Manages environment variables, API keys, and configuration validation.
    Loads configuration from .env file in project root.
    """
    
    def __init__(self, env_path: Optional[str] = None):
        """
        Initialize ConfigManager.
        
        Args:
            env_path: Optional path to .env file. If None, uses project root.
        """
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        if env_path is None:
            env_path = os.path.join(os.getcwd(), '.env')
        
        load_dotenv(dotenv_path=env_path, override=True)
        
        # Validate required environment variables
        self._validate_environment()
        
        # Load configuration
        self._load_config()
    
    def _validate_environment(self) -> None:
        """Validate that required environment variables are present."""
        required_vars = ['USER_KEY', 'DATA_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please create a .env file in your project root with these variables."
            )
    
    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        self.user_key = os.getenv('USER_KEY')
        self.data_api_key = os.getenv('DATA_API_KEY')
        
        # API endpoints
        self.backtest_base_url = f'https://zipline.fin.cloud.ainode.ai/{self.user_key}/'
        self.trading_base_url = f'https://aifapbt.fin.cloud.ainode.ai/{self.user_key}/'
        self.position_base_url = f'https://bitgettrader.fin.cloud.ainode.ai/{self.user_key}/'
        
        self.logger.info("Configuration loaded successfully")
    
    @property
    def api_keys(self) -> Dict[str, str]:
        """Get API keys as dictionary."""
        return {
            'user_key': self.user_key,
            'data_api_key': self.data_api_key
        }
    
    def get_api_endpoint(self, service: str) -> str:
        """
        Get API endpoint for specific service.
        
        Args:
            service: Service name ('backtest', 'trading', 'position')
            
        Returns:
            Base URL for the service
        """
        endpoints = {
            'backtest': self.backtest_base_url,
            'trading': self.trading_base_url,
            'position': self.position_base_url
        }
        
        if service not in endpoints:
            raise ValueError(f"Unknown service: {service}. Available: {list(endpoints.keys())}")
        
        return endpoints[service]
    
    def validate_strategy_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate strategy configuration structure.
        
        Args:
            config: Strategy configuration dictionary
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        required_keys = ['strategy_config']
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")
        
        return True
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ConfigManager(user_key=***{self.user_key[-4:] if self.user_key else 'None'})" 