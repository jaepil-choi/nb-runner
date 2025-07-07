"""
nb-runner modules package

This package provides modular components for strategy verification, backtesting, and trading.
"""

from .config_manager import ConfigManager
from .api_client import APIClient, APIResponse
from .base_strategy import BaseStrategy
from .strategy_manager import StrategyManager
from .backtest_runner import BacktestRunner, BacktestConfig, BacktestResult

__version__ = "1.0.0"
__all__ = [
    "ConfigManager",
    "APIClient",
    "APIResponse",
    "BaseStrategy",
    "StrategyManager",
    "BacktestRunner",
    "BacktestConfig",
    "BacktestResult"
] 