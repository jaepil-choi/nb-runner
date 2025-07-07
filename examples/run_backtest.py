#!/usr/bin/env python3
"""
Backtest Execution Script

This script replaces the functionality of notebook 2 (2.backtest.ipynb)
using the new modular approach with BacktestRunner.

Usage:
    python examples/run_backtest.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.config_manager import ConfigManager
from modules.backtest_runner import BacktestRunner, BacktestConfig
from modules.strategy_manager import StrategyManager

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function to run backtest."""
    setup_logging()
    
    print("🚀 Starting Backtest Execution")
    print("=" * 60)
    
    try:
        # Step 1: Initialize components
        print("\n📋 Step 1: Initializing Components")
        config = ConfigManager()
        backtest_runner = BacktestRunner(config, output_dir="backtest_reports")
        
        print(f"✅ BacktestRunner initialized: {backtest_runner}")
        
        # Step 2: Health check
        print("\n🏥 Step 2: Health Check")
        health_response = backtest_runner.health_check()
        if health_response.success:
            print("✅ Backtest service is healthy")
        else:
            print(f"⚠️ Health check warning: {health_response.error_message}")
        
        # Step 3: Strategy configuration
        print("\n⚙️ Step 3: Setting Up Strategy Configuration")
        strategy_name = "multi_period_momentum"
        trade_type = "future"
        
        # Get strategy configuration template
        strategy_config_template = backtest_runner.get_strategy_config_template(
            strategy_name, trade_type
        )
        
        # Define strategy parameters (equivalent to notebook cell)
        hours = [1, 3, 6]
        strategy_config_params = {
            "rebalancing_config": {
                "rebalancing_interval_hours": 72,
                "minimum_candidates": 0
            },
            "strategy_config": {
                "long_maximum_candidates": 5,
                "short_maximum_candidates": 5,
                "minutes": [int(i * 60) for i in hours]
            }
        }
        
        print(f"✅ Strategy configuration prepared:")
        print(f"   - Strategy: {strategy_name}")
        print(f"   - Trade Type: {trade_type}")
        print(f"   - Hours: {hours}")
        print(f"   - Long candidates: {strategy_config_params['strategy_config']['long_maximum_candidates']}")
        print(f"   - Short candidates: {strategy_config_params['strategy_config']['short_maximum_candidates']}")
        
        # Step 4: Backtest configuration
        print("\n🎯 Step 4: Configuring Backtest Parameters")
        
        # Define backtest parameters (equivalent to notebook configuration)
        backtest_params = {
            "start_date": "2025-03-10",
            "end_date": "2025-03-20",
            "lookback_minutes": 360,
            "initial_capital": 200000.0,
            "leverage": 10,
            "symbols": [
                'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT',
                'ADAUSDT', 'ETCUSDT', 'TRXUSDT', 'DOTUSDT', 'DOGEUSDT'
            ],
            "weight_method": "custom",
            "custom_weights": {
                'BTCUSDT': 0.5,
                'ETHUSDT': 0.2,
                'XRPUSDT': 0.1,
                'BCHUSDT': 0.04,
                'LTCUSDT': 0.04,
                'ADAUSDT': 0.03,
                'ETCUSDT': 0.03,
                'TRXUSDT': 0.03,
                'DOTUSDT': 0.02,
                'DOGEUSDT': 0.01
            },
            "generate_report": True
        }
        
        print(f"✅ Backtest parameters configured:")
        print(f"   - Period: {backtest_params['start_date']} to {backtest_params['end_date']}")
        print(f"   - Capital: ${backtest_params['initial_capital']:,.0f}")
        print(f"   - Leverage: {backtest_params['leverage']}x")
        print(f"   - Symbols: {len(backtest_params['symbols'])} symbols")
        print(f"   - Weight method: {backtest_params['weight_method']}")
        
        # Step 5: Execute backtest
        print("\n🏃 Step 5: Running Backtest")
        print("⏳ This may take several minutes...")
        print("-" * 40)
        
        # Run complete backtest workflow
        result = backtest_runner.run_complete_backtest(
            strategy_name=strategy_name,
            strategy_config_params=strategy_config_params,
            trade_type=trade_type,
            **backtest_params
        )
        
        # Step 6: Display results
        print("\n📊 Step 6: Backtest Results")
        backtest_runner.print_backtest_result(result)
        
        # Additional result analysis
        if result.success:
            print("\n🎉 Backtest completed successfully!")
            
            if result.html_file_path:
                print(f"📄 HTML report saved to: {result.html_file_path}")
                print("💡 Open this file in your browser to view detailed results")
            
            # Show strategy upload status
            uploaded_strategies = backtest_runner.list_uploaded_strategies()
            print(f"\n📋 Uploaded strategies: {uploaded_strategies}")
            
        else:
            print(f"\n❌ Backtest failed: {result.error_message}")
            print("💡 Check your configuration and try again")
            return 1
        
        print("\n✅ Backtest execution completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during backtest execution: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 