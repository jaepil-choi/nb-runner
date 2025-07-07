# nb-runner Examples

This directory contains example scripts that demonstrate how to use the new modular nb-runner system.

## 🚀 Quick Start

### 1. Set up Environment

Create a `.env` file in your project root with your API keys:

```env
# Your NeoMatrixAI User Key
USER_KEY=your_user_key_here

# Data API Key  
DATA_API_KEY=your_data_api_key_here

# Optional: Set log level
LOG_LEVEL=INFO
```

### 2. Install Dependencies

```bash
pip install pandas numpy requests python-dotenv
```

### 3. Run Strategy Verification

```bash
python examples/verify_strategy.py
```

## 📂 Available Examples

### `verify_strategy.py`
- **Purpose**: Replaces notebook 1 functionality
- **Function**: Verifies that your strategy is implemented correctly
- **Usage**: `python examples/verify_strategy.py`

### `run_backtest.py`
- **Purpose**: Replaces notebook 2 functionality
- **Function**: Runs backtests with full configuration options
- **Usage**: `python examples/run_backtest.py`
- **Features**: Strategy upload, backtest execution, HTML report generation

### `advanced_backtest.py`
- **Purpose**: Advanced backtesting scenarios
- **Function**: Demonstrates multiple backtest configurations and comparisons
- **Usage**: `python examples/advanced_backtest.py`
- **Features**: Quick tests, comprehensive analysis, custom weight allocation

## 🔧 Creating Your Own Strategy

### Step 1: Create Strategy Directory Structure

```
strategy/
├── future/  # or spot/
│   └── your_strategy_name/
│       ├── __init__.py
│       ├── strategy.py     # Your strategy class
│       └── config.py       # Strategy configuration
```

### Step 2: Implement Strategy Class

```python
# strategy/future/your_strategy_name/strategy.py
import pandas as pd
from typing import Dict, Any, List, Tuple
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.base_strategy import BaseStrategy

class YourStrategy(BaseStrategy):
    def validate_config(self) -> bool:
        # Validate your strategy configuration
        return True
    
    def run(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        # Implement your strategy logic
        long_candidates = []
        short_candidates = []
        return long_candidates, short_candidates

# Legacy compatibility
def strategy(df: pd.DataFrame, config_dict: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    strategy_instance = YourStrategy(config_dict)
    return strategy_instance.run(df)
```

### Step 3: Create Configuration

```python
# strategy/future/your_strategy_name/config.py
strategy_config = {
    "param1": "value1",
    "param2": "value2"
}

rebalancing_config = {
    "rebalancing_interval_hours": 3,
    "minimum_candidates": 0
}
```

### Step 4: Test Your Strategy

```python
from modules.config_manager import ConfigManager
from modules.strategy_manager import StrategyManager

# Initialize
config = ConfigManager()
strategy_manager = StrategyManager(config)

# Load and test
strategy = strategy_manager.create_strategy_instance("your_strategy_name", "future")
long_candidates, short_candidates = strategy.run(your_data)
```

### Step 5: Run Backtests

```python
from modules.backtest_runner import BacktestRunner

# Initialize backtest runner
backtest_runner = BacktestRunner(config, output_dir="my_backtests")

# Define strategy configuration
strategy_config = {
    "rebalancing_config": {"rebalancing_interval_hours": 24, "minimum_candidates": 0},
    "strategy_config": {"param1": "value1", "param2": "value2"}
}

# Run backtest
result = backtest_runner.run_complete_backtest(
    strategy_name="your_strategy_name",
    strategy_config_params=strategy_config,
    start_date="2025-03-01",
    end_date="2025-03-31",
    initial_capital=200000.0,
    symbols=['BTCUSDT', 'ETHUSDT', 'XRPUSDT']
)

# Check results
if result.success:
    print(f"Backtest successful! HTML report: {result.html_file_path}")
else:
    print(f"Backtest failed: {result.error_message}")
```

## 🎯 Key Benefits

1. **Modular Design**: Each component is independent and reusable
2. **Type Safety**: Proper type hints and validation
3. **Easy Testing**: Each strategy can be tested in isolation
4. **Backward Compatibility**: Old function-based strategies still work
5. **Local Development**: Full support for local environment with `.env` files

## 🔄 Migration from Notebooks

| Old Notebook | New Approach |
|-------------|-------------|
| `1.strategy_verify_test.ipynb` | `python examples/verify_strategy.py` |
| `2.backtest.ipynb` | `python examples/run_backtest.py` |
| `3.trade.ipynb` | Use `TradeManager` class (coming soon) |

### 📊 Backtest Configuration Examples

**Equal Weight Strategy:**
```python
backtest_params = {
    "weight_method": "equal",
    "symbols": ['BTCUSDT', 'ETHUSDT', 'XRPUSDT']
}
```

**Custom Weight Strategy:**
```python
backtest_params = {
    "weight_method": "custom",
    "custom_weights": {
        'BTCUSDT': 0.5,
        'ETHUSDT': 0.3,
        'XRPUSDT': 0.2
    }
}
```

**Long/Short Split:**
```python
backtest_params = {
    "weight_method": "split"  # Auto-splits between long and short positions
}
```

## 📞 Support

For issues or questions, please check the main project README or create an issue in the repository. 