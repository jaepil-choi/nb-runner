"""
Strategy Manager for nb-runner

Handles dynamic strategy loading, validation, and management.
"""

import os
import importlib
import importlib.util
import sys
from typing import Dict, Any, List, Optional, Type, Tuple
import logging
from pathlib import Path

from .base_strategy import BaseStrategy
from .config_manager import ConfigManager

class StrategyManager:
    """
    Strategy management system for nb-runner.
    
    Handles dynamic loading, validation, and execution of trading strategies.
    """
    
    def __init__(self, config_manager: ConfigManager, strategy_base_path: str = "strategy"):
        """
        Initialize StrategyManager.
        
        Args:
            config_manager: ConfigManager instance
            strategy_base_path: Base path to strategy directory
        """
        self.config = config_manager
        self.strategy_base_path = Path(strategy_base_path)
        self.logger = logging.getLogger(__name__)
        
        # Registry of loaded strategies
        self._strategy_registry: Dict[str, Dict[str, Any]] = {}
        
        # Discover available strategies
        self._discover_strategies()
    
    def _discover_strategies(self) -> None:
        """Discover available strategies in the strategy directory."""
        if not self.strategy_base_path.exists():
            self.logger.warning(f"Strategy directory does not exist: {self.strategy_base_path}")
            return
        
        self.logger.info(f"Discovering strategies in {self.strategy_base_path}")
        
        # Look for strategy directories
        for trade_type in ['future', 'spot']:
            trade_type_path = self.strategy_base_path / trade_type
            if not trade_type_path.exists():
                continue
            
            for strategy_dir in trade_type_path.iterdir():
                if strategy_dir.is_dir() and not strategy_dir.name.startswith('.'):
                    self._register_strategy(strategy_dir, trade_type)
    
    def _register_strategy(self, strategy_path: Path, trade_type: str) -> None:
        """
        Register a strategy from its directory.
        
        Args:
            strategy_path: Path to strategy directory
            trade_type: 'future' or 'spot'
        """
        strategy_name = strategy_path.name
        
        # Look for strategy.py file
        strategy_file = strategy_path / 'strategy.py'
        if not strategy_file.exists():
            # Fallback to old naming convention
            strategy_file = strategy_path / f'{strategy_name}.py'
            if not strategy_file.exists():
                self.logger.warning(f"No strategy file found in {strategy_path}")
                return
        
        # Look for config.py file
        config_file = strategy_path / 'config.py'
        if not config_file.exists():
            # Fallback to old naming convention
            config_file = strategy_path / f'{strategy_name}_config.py'
            if not config_file.exists():
                self.logger.warning(f"No config file found in {strategy_path}")
                return
        
        # Register strategy
        strategy_key = f"{trade_type}.{strategy_name}"
        self._strategy_registry[strategy_key] = {
            'name': strategy_name,
            'trade_type': trade_type,
            'strategy_file': strategy_file,
            'config_file': config_file,
            'path': strategy_path
        }
        
        self.logger.info(f"Registered strategy: {strategy_key}")
    
    def get_available_strategies(self) -> Dict[str, List[str]]:
        """
        Get list of available strategies by trade type.
        
        Returns:
            Dictionary with 'future' and 'spot' keys containing strategy lists
        """
        strategies = {'future': [], 'spot': []}
        
        for strategy_key, info in self._strategy_registry.items():
            trade_type = info['trade_type']
            strategy_name = info['name']
            strategies[trade_type].append(strategy_name)
        
        return strategies
    
    def load_strategy_config(self, strategy_name: str, trade_type: str) -> Dict[str, Any]:
        """
        Load strategy configuration from config file.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            Strategy configuration dictionary
        """
        strategy_key = f"{trade_type}.{strategy_name}"
        
        if strategy_key not in self._strategy_registry:
            raise ValueError(f"Strategy not found: {strategy_key}")
        
        config_file = self._strategy_registry[strategy_key]['config_file']
        
        # Load config module
        spec = importlib.util.spec_from_file_location("strategy_config", config_file)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Extract configuration
        config = {}
        if hasattr(config_module, 'strategy_config'):
            config['strategy_config'] = config_module.strategy_config
        if hasattr(config_module, 'rebalancing_config'):
            config['rebalancing_config'] = config_module.rebalancing_config
        if hasattr(config_module, 'system_config'):
            config['system_config'] = config_module.system_config
        
        return config
    
    def load_strategy_class(self, strategy_name: str, trade_type: str) -> Type[BaseStrategy]:
        """
        Load strategy class from strategy file.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            Strategy class that inherits from BaseStrategy
        """
        strategy_key = f"{trade_type}.{strategy_name}"
        
        if strategy_key not in self._strategy_registry:
            raise ValueError(f"Strategy not found: {strategy_key}")
        
        strategy_file = self._strategy_registry[strategy_key]['strategy_file']
        
        # Load strategy module
        spec = importlib.util.spec_from_file_location("strategy_module", strategy_file)
        strategy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(strategy_module)
        
        # Look for strategy class
        strategy_class = None
        for attr_name in dir(strategy_module):
            attr = getattr(strategy_module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, BaseStrategy) and 
                attr is not BaseStrategy):
                strategy_class = attr
                break
        
        if strategy_class is None:
            raise ValueError(f"No BaseStrategy subclass found in {strategy_file}")
        
        return strategy_class
    
    def create_strategy_instance(
        self, 
        strategy_name: str, 
        trade_type: str, 
        config_override: Optional[Dict[str, Any]] = None
    ) -> BaseStrategy:
        """
        Create strategy instance with configuration.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            config_override: Optional config override
            
        Returns:
            Initialized strategy instance
        """
        # Load strategy class
        strategy_class = self.load_strategy_class(strategy_name, trade_type)
        
        # Load configuration
        config = self.load_strategy_config(strategy_name, trade_type)
        
        # Apply config override if provided
        if config_override:
            config.update(config_override)
        
        # Create and return strategy instance
        return strategy_class(config)
    
    def load_legacy_strategy(self, strategy_name: str, trade_type: str) -> callable:
        """
        Load strategy as legacy function for backward compatibility.
        
        This method handles both new class-based strategies and old function-based strategies.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            Strategy function with signature: (df, config_dict) -> (long_candidates, short_candidates)
        """
        strategy_key = f"{trade_type}.{strategy_name}"
        
        if strategy_key not in self._strategy_registry:
            raise ValueError(f"Strategy not found: {strategy_key}")
        
        strategy_file = self._strategy_registry[strategy_key]['strategy_file']
        
        # Load strategy module
        spec = importlib.util.spec_from_file_location("strategy_module", strategy_file)
        strategy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(strategy_module)
        
        # Check if it's a new class-based strategy
        strategy_class = None
        for attr_name in dir(strategy_module):
            attr = getattr(strategy_module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, BaseStrategy) and 
                attr is not BaseStrategy):
                strategy_class = attr
                break
        
        if strategy_class:
            # New class-based strategy - create wrapper function
            def strategy_function(df, config_dict):
                strategy = strategy_class(config_dict)
                return strategy.run(df)
            return strategy_function
        
        # Old function-based strategy
        if hasattr(strategy_module, 'strategy'):
            return strategy_module.strategy
        else:
            raise ValueError(f"No strategy function or class found in {strategy_file}")
    
    def validate_strategy(self, strategy_name: str, trade_type: str) -> bool:
        """
        Validate strategy implementation.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            True if strategy is valid
        """
        try:
            # Try to create strategy instance
            config = self.load_strategy_config(strategy_name, trade_type)
            strategy = self.create_strategy_instance(strategy_name, trade_type)
            
            # Validate strategy info
            info = strategy.get_strategy_info()
            required_info_keys = ['name', 'config', 'required_lookback']
            
            for key in required_info_keys:
                if key not in info:
                    raise ValueError(f"Strategy info missing key: {key}")
            
            self.logger.info(f"Strategy validation passed: {trade_type}.{strategy_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Strategy validation failed for {trade_type}.{strategy_name}: {e}")
            return False
    
    def get_strategy_info(self, strategy_name: str, trade_type: str) -> Dict[str, Any]:
        """
        Get detailed strategy information.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            Strategy information dictionary
        """
        strategy_key = f"{trade_type}.{strategy_name}"
        
        if strategy_key not in self._strategy_registry:
            raise ValueError(f"Strategy not found: {strategy_key}")
        
        registry_info = self._strategy_registry[strategy_key]
        
        # Try to get strategy-specific info
        try:
            strategy = self.create_strategy_instance(strategy_name, trade_type)
            strategy_info = strategy.get_strategy_info()
        except Exception as e:
            strategy_info = {'error': str(e)}
        
        return {
            'registry_info': registry_info,
            'strategy_info': strategy_info
        }
    
    def export_strategy_for_upload(self, strategy_name: str, trade_type: str) -> str:
        """
        Get strategy file path for upload to server.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            Path to strategy file
        """
        strategy_key = f"{trade_type}.{strategy_name}"
        
        if strategy_key not in self._strategy_registry:
            raise ValueError(f"Strategy not found: {strategy_key}")
        
        return str(self._strategy_registry[strategy_key]['strategy_file'])
    
    def export_config_for_upload(self, strategy_name: str, trade_type: str) -> str:
        """
        Get config file path for upload to server.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            Path to config file
        """
        strategy_key = f"{trade_type}.{strategy_name}"
        
        if strategy_key not in self._strategy_registry:
            raise ValueError(f"Strategy not found: {strategy_key}")
        
        return str(self._strategy_registry[strategy_key]['config_file']) 