#!/usr/bin/env python3
"""
Advanced Backtest Example

This script demonstrates advanced usage of BacktestRunner with different
configuration patterns and customization options.

Usage:
    python examples/advanced_backtest.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.config_manager import ConfigManager
from modules.backtest_runner import BacktestRunner, BacktestConfig, BacktestResult
from modules.strategy_manager import StrategyManager

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def run_quick_backtest(backtest_runner: BacktestRunner) -> BacktestResult:
    """Run a quick backtest with minimal configuration."""
    print("\n🚀 Running Quick Backtest (logs only)")
    print("-" * 40)
    
    # Minimal configuration
    strategy_config = {
        "rebalancing_config": {
            "rebalancing_interval_hours": 24,
            "minimum_candidates": 0
        },
        "strategy_config": {
            "long_maximum_candidates": 2,
            "short_maximum_candidates": 1,
            "minutes": [60, 180, 360]  # 1h, 3h, 6h
        }
    }
    
    # Quick backtest parameters
    backtest_params = {
        "start_date": "2025-03-15",
        "end_date": "2025-03-17",  # Short period for quick test
        "initial_capital": 100000.0,
        "leverage": 5,
        "symbols": ['BTCUSDT', 'ETHUSDT', 'XRPUSDT'],  # Few symbols
        "weight_method": "equal",
        "generate_report": False  # Logs only for speed
    }
    
    return backtest_runner.run_complete_backtest(
        strategy_name="multi_period_momentum",
        strategy_config_params=strategy_config,
        **backtest_params
    )

def run_comprehensive_backtest(backtest_runner: BacktestRunner) -> BacktestResult:
    """Run a comprehensive backtest with full configuration."""
    print("\n📊 Running Comprehensive Backtest (with HTML report)")
    print("-" * 50)
    
    # Comprehensive strategy configuration
    strategy_config = {
        "rebalancing_config": {
            "rebalancing_interval_hours": 72,
            "minimum_candidates": 1
        },
        "strategy_config": {
            "long_maximum_candidates": 8,
            "short_maximum_candidates": 5,
            "minutes": [30, 60, 120, 240, 480]  # Multiple timeframes
        }
    }
    
    # Comprehensive backtest parameters
    backtest_params = {
        "start_date": "2025-03-01",
        "end_date": "2025-03-31",  # Full month
        "initial_capital": 500000.0,
        "leverage": 15,
        "symbols": [
            'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT',
            'ADAUSDT', 'ETCUSDT', 'TRXUSDT', 'DOTUSDT', 'DOGEUSDT',
            'SOLUSDT', 'BNBUSDT', 'ICPUSDT', 'FILUSDT', 'XLMUSDT'
        ],
        "weight_method": "split",  # Auto split between long/short
        "generate_report": True
    }
    
    return backtest_runner.run_complete_backtest(
        strategy_name="multi_period_momentum",
        strategy_config_params=strategy_config,
        **backtest_params
    )

def run_custom_weight_backtest(backtest_runner: BacktestRunner) -> BacktestResult:
    """Run a backtest with custom weight allocation."""
    print("\n⚖️ Running Custom Weight Backtest")
    print("-" * 40)
    
    # Strategy configuration
    strategy_config = {
        "rebalancing_config": {
            "rebalancing_interval_hours": 48,
            "minimum_candidates": 0
        },
        "strategy_config": {
            "long_maximum_candidates": 5,
            "short_maximum_candidates": 3,
            "minutes": [60, 240, 720]  # 1h, 4h, 12h
        }
    }
    
    # Custom weight allocation (must sum to 1.0)
    custom_weights = {
        'BTCUSDT': 0.40,   # 40% Bitcoin
        'ETHUSDT': 0.25,   # 25% Ethereum
        'XRPUSDT': 0.15,   # 15% XRP
        'SOLUSDT': 0.10,   # 10% Solana
        'ADAUSDT': 0.05,   # 5% Cardano
        'DOTUSDT': 0.05    # 5% Polkadot
    }
    
    backtest_params = {
        "start_date": "2025-03-10",
        "end_date": "2025-03-20",
        "initial_capital": 300000.0,
        "leverage": 8,
        "symbols": list(custom_weights.keys()),
        "weight_method": "custom",
        "custom_weights": custom_weights,
        "generate_report": True
    }
    
    return backtest_runner.run_complete_backtest(
        strategy_name="multi_period_momentum",
        strategy_config_params=strategy_config,
        **backtest_params
    )

def compare_backtest_results(results: list[BacktestResult]):
    """Compare multiple backtest results."""
    print("\n📈 Backtest Comparison")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.strategy_name} - {result.execution_time.strftime('%H:%M:%S')}")
        print(f"   Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        print(f"   Report: {result.report_type}")
        
        if result.html_file_path:
            print(f"   HTML: {Path(result.html_file_path).name}")
        
        if not result.success:
            print(f"   Error: {result.error_message}")

def main():
    """Main function demonstrating advanced backtest usage."""
    setup_logging()
    
    print("🚀 Advanced Backtest Runner Demo")
    print("=" * 60)
    
    try:
        # Initialize components
        print("\n📋 Initializing Components")
        config = ConfigManager()
        backtest_runner = BacktestRunner(config, output_dir="advanced_backtest_reports")
        
        print(f"✅ BacktestRunner initialized")
        print(f"   Output directory: {backtest_runner.output_dir}")
        
        # Health check
        health_response = backtest_runner.health_check()
        if not health_response.success:
            print(f"⚠️ Health check failed: {health_response.error_message}")
            print("Continuing anyway...")
        
        # Store results for comparison
        results = []
        
        # Run different types of backtests
        print("\n" + "="*60)
        print("RUNNING MULTIPLE BACKTEST SCENARIOS")
        print("="*60)
        
        # 1. Quick backtest
        try:
            quick_result = run_quick_backtest(backtest_runner)
            results.append(quick_result)
            if quick_result.success:
                print("✅ Quick backtest completed")
            else:
                print(f"❌ Quick backtest failed: {quick_result.error_message}")
        except Exception as e:
            print(f"❌ Quick backtest error: {e}")
        
        # 2. Comprehensive backtest
        try:
            comprehensive_result = run_comprehensive_backtest(backtest_runner)
            results.append(comprehensive_result)
            if comprehensive_result.success:
                print("✅ Comprehensive backtest completed")
            else:
                print(f"❌ Comprehensive backtest failed: {comprehensive_result.error_message}")
        except Exception as e:
            print(f"❌ Comprehensive backtest error: {e}")
        
        # 3. Custom weight backtest
        try:
            custom_result = run_custom_weight_backtest(backtest_runner)
            results.append(custom_result)
            if custom_result.success:
                print("✅ Custom weight backtest completed")
            else:
                print(f"❌ Custom weight backtest failed: {custom_result.error_message}")
        except Exception as e:
            print(f"❌ Custom weight backtest error: {e}")
        
        # Compare results
        if results:
            compare_backtest_results(results)
        
        # Show uploaded strategies
        uploaded = backtest_runner.list_uploaded_strategies()
        print(f"\n📋 Uploaded strategies: {uploaded}")
        
        # Summary
        successful_runs = sum(1 for r in results if r.success)
        print(f"\n🎯 Summary: {successful_runs}/{len(results)} backtests successful")
        
        if successful_runs > 0:
            print(f"📁 Check {backtest_runner.output_dir} for HTML reports")
        
        print("\n✅ Advanced backtest demo completed!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during advanced backtest demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 