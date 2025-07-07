"""
Base Strategy Interface for nb-runner

Abstract base class that all strategies must inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import pandas as pd
import logging

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All strategies must inherit from this class and implement the required methods.
    This ensures consistent interface across all strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration.
        
        Args:
            config: Strategy configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validate configuration on initialization
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate strategy configuration.
        
        Must be implemented by each strategy to validate its specific parameters.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def run(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Execute strategy on given data.
        
        Args:
            df: Price time series data with datetime index and symbol columns
            
        Returns:
            Tuple of (long_candidates, short_candidates)
            - long_candidates: List of symbols to buy
            - short_candidates: List of symbols to sell
        """
        pass
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data before strategy execution.
        
        Override this method if your strategy needs special data preprocessing.
        
        Args:
            df: Raw price data
            
        Returns:
            Preprocessed data
        """
        # Default implementation - just validate input
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        
        if df.empty:
            raise ValueError("Input DataFrame is empty")
        
        return df
    
    def postprocess_results(
        self, 
        long_candidates: List[str], 
        short_candidates: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Postprocess strategy results.
        
        Override this method if your strategy needs result postprocessing.
        
        Args:
            long_candidates: Raw long candidates
            short_candidates: Raw short candidates
            
        Returns:
            Processed (long_candidates, short_candidates)
        """
        return long_candidates, short_candidates
    
    def get_required_lookback_periods(self) -> int:
        """
        Get minimum historical data periods required by strategy.
        
        Override this method to specify your strategy's data requirements.
        
        Returns:
            Number of periods required
        """
        return 0
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get strategy information and metadata.
        
        Returns:
            Dictionary with strategy information
        """
        return {
            'name': self.__class__.__name__,
            'config': self.config,
            'required_lookback': self.get_required_lookback_periods(),
            'description': self.__doc__ or 'No description available'
        }
    
    def __str__(self) -> str:
        """String representation of strategy."""
        return f"{self.__class__.__name__}(config={self.config})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()


class SimpleStrategy(BaseStrategy):
    """
    Simple strategy implementation for testing and examples.
    
    This strategy can be used as a template for creating new strategies.
    """
    
    def validate_config(self) -> bool:
        """Validate simple strategy configuration."""
        required_keys = ['strategy_config']
        
        if 'strategy_config' not in self.config:
            raise ValueError("Missing 'strategy_config' in configuration")
        
        return True
    
    def run(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Simple strategy: return first and last columns as long/short candidates.
        
        This is a placeholder implementation for testing.
        """
        df = self.preprocess_data(df)
        
        if len(df.columns) < 2:
            return [], []
        
        # Simple logic: first symbol long, last symbol short
        long_candidates = [df.columns[0]]
        short_candidates = [df.columns[-1]]
        
        return self.postprocess_results(long_candidates, short_candidates)


# Legacy function wrapper for backward compatibility
def create_strategy_function(strategy_class: BaseStrategy) -> callable:
    """
    Create a legacy strategy function from a strategy class.
    
    This allows using new class-based strategies in contexts that expect
    the old function-based interface.
    
    Args:
        strategy_class: BaseStrategy subclass instance
        
    Returns:
        Function that matches the old strategy(df, config_dict) signature
    """
    def strategy_function(df: pd.DataFrame, config_dict: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Legacy strategy function wrapper."""
        # Create strategy instance with config
        strategy = strategy_class(config_dict)
        return strategy.run(df)
    
    return strategy_function 