#!/usr/bin/env python3
"""
Strategy Verification Script

This script replaces the functionality of notebook 1 (strategy_verify_test.ipynb)
using the new modular approach.

Usage:
    python examples/verify_strategy.py
"""

import os
import sys
import pandas as pd
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.config_manager import ConfigManager
from modules.strategy_manager import StrategyManager

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_sample_data():
    """Create sample data for testing."""
    # In a real scenario, you would load this from a file or API
    import numpy as np
    
    dates = pd.date_range('2024-01-01', periods=500, freq='1min')
    symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT']
    
    # Generate sample price data (random walk)
    np.random.seed(42)  # For reproducible results
    
    data = {}
    for symbol in symbols:
        # Start with a base price
        base_price = np.random.uniform(100, 50000)
        
        # Generate random walk
        returns = np.random.normal(0, 0.01, len(dates))
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        data[symbol] = prices
    
    df = pd.DataFrame(data, index=dates)
    return df

def main():
    """Main function to verify strategy."""
    setup_logging()
    
    print("🚀 Starting Strategy Verification")
    print("=" * 50)
    
    try:
        # Step 1: Initialize configuration
        print("\n📋 Step 1: Loading Configuration")
        config = ConfigManager()
        print(f"✅ Configuration loaded: {config}")
        
        # Step 2: Initialize strategy manager
        print("\n📂 Step 2: Initializing Strategy Manager")
        strategy_manager = StrategyManager(config)
        
        # List available strategies
        available_strategies = strategy_manager.get_available_strategies()
        print(f"✅ Available strategies: {available_strategies}")
        
        # Step 3: Load and test strategy
        print("\n🎯 Step 3: Loading Strategy")
        strategy_name = "multi_period_momentum"
        trade_type = "future"
        
        # Validate strategy
        is_valid = strategy_manager.validate_strategy(strategy_name, trade_type)
        print(f"✅ Strategy validation: {'PASSED' if is_valid else 'FAILED'}")
        
        if not is_valid:
            print("❌ Strategy validation failed. Please check your strategy implementation.")
            return
        
        # Create strategy instance
        strategy = strategy_manager.create_strategy_instance(strategy_name, trade_type)
        print(f"✅ Strategy instance created: {strategy}")
        
        # Step 4: Test with sample data
        print("\n📊 Step 4: Testing Strategy with Sample Data")
        sample_data = create_sample_data()
        print(f"✅ Sample data created: {sample_data.shape}")
        print(f"   - Date range: {sample_data.index[0]} to {sample_data.index[-1]}")
        print(f"   - Symbols: {list(sample_data.columns)}")
        
        # Run strategy
        print("\n🏃 Step 5: Running Strategy")
        long_candidates, short_candidates = strategy.run(sample_data)
        
        print(f"✅ Strategy execution completed!")
        print(f"   - Long candidates: {long_candidates}")
        print(f"   - Short candidates: {short_candidates}")
        
        # Step 6: Display strategy information
        print("\n📝 Step 6: Strategy Information")
        strategy_info = strategy.get_strategy_info()
        print(f"   - Name: {strategy_info['name']}")
        print(f"   - Required lookback: {strategy_info['required_lookback']} periods")
        print(f"   - Description: {strategy_info['description'][:100]}...")
        
        print("\n✅ Strategy verification completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during strategy verification: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 