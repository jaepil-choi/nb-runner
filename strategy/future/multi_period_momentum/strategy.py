"""
Multi-Period Momentum Strategy Implementation

A strategy that calculates momentum over multiple time periods and returns
a ranking of the top and bottom stocks for long and short positions.
"""

import pandas as pd
from typing import Dict, Any, List, Tuple
import sys
import os

# Add modules to path for import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.base_strategy import BaseStrategy

class MultiPeriodMomentumStrategy(BaseStrategy):
    """
    Multi-Period Momentum Strategy
    
    This strategy calculates momentum over multiple time periods (minutes) 
    and returns a ranking of the top and bottom stocks for long and short positions.
    
    The strategy uses a weighted average of momentum scores calculated over different
    time horizons to determine which assets to go long or short.
    """
    
    def validate_config(self) -> bool:
        """
        Validate the strategy configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if 'strategy_config' not in self.config:
            raise ValueError("Missing 'strategy_config' in configuration")
        
        strategy_config = self.config['strategy_config']
        
        # Check required parameters
        required_params = ['minutes', 'long_maximum_candidates', 'short_maximum_candidates']
        for param in required_params:
            if param not in strategy_config:
                raise ValueError(f"Missing required parameter: {param}")
        
        # Validate parameter types and values
        minutes = strategy_config['minutes']
        if not isinstance(minutes, list) or len(minutes) == 0:
            raise ValueError("'minutes' must be a non-empty list")
        
        if not all(isinstance(m, int) and m > 0 for m in minutes):
            raise ValueError("All values in 'minutes' must be positive integers")
        
        long_max = strategy_config['long_maximum_candidates']
        short_max = strategy_config['short_maximum_candidates']
        
        if not isinstance(long_max, int) or long_max < 0:
            raise ValueError("'long_maximum_candidates' must be a non-negative integer")
        
        if not isinstance(short_max, int) or short_max < 0:
            raise ValueError("'short_maximum_candidates' must be a non-negative integer")
        
        return True
    
    def get_required_lookback_periods(self) -> int:
        """
        Get minimum historical data periods required by strategy.
        
        Returns:
            Maximum value from the minutes parameter
        """
        strategy_config = self.config.get('strategy_config', {})
        minutes = strategy_config.get('minutes', [])
        
        if not minutes:
            return 0
        
        return max(minutes)
    
    def run(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """
        Execute the multi-period momentum strategy.
        
        Args:
            df: Price time series data with datetime index and symbol columns
            
        Returns:
            Tuple of (long_candidates, short_candidates)
        """
        # Preprocess data
        df = self.preprocess_data(df)
        
        # Get strategy parameters
        strategy_config = self.config['strategy_config']
        periods = strategy_config['minutes']
        long_maximum_candidates = strategy_config['long_maximum_candidates']
        short_maximum_candidates = strategy_config['short_maximum_candidates']
        
        # Calculate momentum scores
        momentum = self._calculate_momentum(df, periods)
        
        # Get the most recent momentum scores
        if momentum.empty:
            return [], []
        
        momentum_scores = momentum.iloc[-1]
        
        # Rank symbols by momentum
        ranked_symbols = momentum_scores.sort_values(ascending=False)
        
        # Select top and bottom candidates
        long_candidates = list(ranked_symbols.head(long_maximum_candidates).index)
        short_candidates = list(ranked_symbols.tail(short_maximum_candidates).index)
        
        return self.postprocess_results(long_candidates, short_candidates)
    
    def _calculate_momentum(self, df: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
        """
        Calculate momentum scores over multiple periods.
        
        Args:
            df: Price data DataFrame
            periods: List of time periods (in minutes)
            
        Returns:
            DataFrame with momentum scores
        """
        momentum = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)
        M = len(periods)
        
        # Calculate momentum for each symbol and time point
        for col in df.columns:
            for t in range(max(periods), len(df)):
                summation = 0
                for h in periods:
                    if t - h >= 0:
                        # Calculate raw return
                        raw_return = df[col].iloc[t] / df[col].iloc[t - h] - 1
                        # Calculate annualized return
                        adjusted_return = (1 + raw_return) ** (1 / h) - 1
                        summation += adjusted_return
                
                momentum.loc[momentum.index[t], col] = summation / M
        
        return momentum
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data for momentum calculation.
        
        Args:
            df: Raw price data
            
        Returns:
            Preprocessed data
        """
        df = super().preprocess_data(df)
        
        # Check if we have enough data for the longest period
        min_required_periods = self.get_required_lookback_periods()
        if len(df) < min_required_periods:
            raise ValueError(
                f"Insufficient data: need at least {min_required_periods} periods, "
                f"but got {len(df)}"
            )
        
        # Remove any columns with all NaN values
        df = df.dropna(axis=1, how='all')
        
        if df.empty:
            raise ValueError("No valid data after preprocessing")
        
        return df
    
    def postprocess_results(
        self, 
        long_candidates: List[str], 
        short_candidates: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Postprocess strategy results.
        
        Args:
            long_candidates: Raw long candidates
            short_candidates: Raw short candidates
            
        Returns:
            Processed results
        """
        # Remove any duplicates between long and short candidates
        # Priority: long candidates take precedence
        short_candidates = [symbol for symbol in short_candidates 
                          if symbol not in long_candidates]
        
        return long_candidates, short_candidates


# Legacy function for backward compatibility
def strategy(df: pd.DataFrame, config_dict: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Legacy strategy function for backward compatibility.
    
    Args:
        df: Price time series data
        config_dict: Configuration dictionary
        
    Returns:
        Tuple of (long_candidates, short_candidates)
    """
    strategy_instance = MultiPeriodMomentumStrategy(config_dict)
    return strategy_instance.run(df) 