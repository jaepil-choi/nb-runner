"""
Backtest Runner for nb-runner

Handles backtesting operations including strategy upload, configuration, execution, and result management.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field

from .config_manager import ConfigManager
from .api_client import APIClient, APIResponse
from .strategy_manager import StrategyManager

@dataclass
class BacktestConfig:
    """Configuration for backtest execution."""
    strategy_name: str
    trade_type: str = "future"
    start_date: str = "2025-03-10"
    end_date: str = "2025-03-20"
    lookback_minutes: int = 360
    initial_capital: float = 200000.0
    leverage: int = 10
    symbols: List[str] = field(default_factory=lambda: [
        'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT',
        'ADAUSDT', 'ETCUSDT', 'TRXUSDT', 'DOTUSDT', 'DOGEUSDT'
    ])
    calendar: str = "24/7"
    frequency: str = "minute"
    weight_method: str = "equal"  # "equal", "split", "custom"
    custom_weights: Optional[Dict[str, float]] = None
    generate_report: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.weight_method == "custom" and not self.custom_weights:
            raise ValueError("custom_weights is required when weight_method is 'custom'")
        
        if self.custom_weights:
            total_weight = sum(self.custom_weights.values())
            if abs(total_weight - 1.0) > 0.001:
                raise ValueError(f"Custom weights must sum to 1.0, got {total_weight}")

@dataclass
class BacktestResult:
    """Result of backtest execution."""
    success: bool
    strategy_name: str
    execution_time: datetime
    report_type: str  # "html" or "logs_only"
    logs: str
    stdout: Optional[str] = None
    html_content: Optional[str] = None
    html_file_path: Optional[str] = None
    error_message: Optional[str] = None

class BacktestRunner:
    """
    Backtest execution manager for nb-runner system.
    
    Handles strategy upload, configuration, execution, and result management.
    """
    
    def __init__(self, config_manager: ConfigManager, output_dir: str = "backtest_reports"):
        """
        Initialize BacktestRunner.
        
        Args:
            config_manager: ConfigManager instance
            output_dir: Directory to save backtest reports
        """
        self.config = config_manager
        self.api_client = APIClient(config_manager)
        self.strategy_manager = StrategyManager(config_manager)
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track uploaded strategies
        self._uploaded_strategies: Dict[str, bool] = {}
    
    def health_check(self) -> APIResponse:
        """
        Check backtest service health.
        
        Returns:
            APIResponse with health status
        """
        return self.api_client.health_check('backtest')
    
    def upload_strategy(self, strategy_name: str, trade_type: str = "future") -> APIResponse:
        """
        Upload strategy to backtest server.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            APIResponse with upload result
        """
        try:
            # Get strategy file path
            strategy_file_path = self.strategy_manager.export_strategy_for_upload(
                strategy_name, trade_type
            )
            
            # Upload strategy
            response = self.api_client.upload_strategy(
                strategy_file_path=strategy_file_path,
                strategy_name=strategy_name,
                trade_type=trade_type,
                service="backtest"
            )
            
            if response.success:
                strategy_key = f"{trade_type}.{strategy_name}"
                self._uploaded_strategies[strategy_key] = True
                self.logger.info(f"Strategy uploaded successfully: {strategy_key}")
            else:
                self.logger.error(f"Failed to upload strategy: {response.error_message}")
            
            return response
            
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                status_code=500,
                error_message=f"Upload error: {str(e)}"
            )
    
    def check_strategy_upload(self, strategy_name: str, trade_type: str = "future") -> APIResponse:
        """
        Check if strategy is uploaded on server.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            APIResponse with strategy info
        """
        return self.api_client.check_uploaded_strategy(
            strategy_name, trade_type, "backtest"
        )
    
    def create_backtest_config(
        self,
        strategy_name: str,
        strategy_config_params: Dict[str, Any],
        **kwargs
    ) -> BacktestConfig:
        """
        Create backtest configuration.
        
        Args:
            strategy_name: Name of the strategy
            strategy_config_params: Strategy-specific configuration
            **kwargs: Additional backtest parameters
            
        Returns:
            BacktestConfig instance
        """
        config_dict = {
            'strategy_name': strategy_name,
            'strategy_config_params': strategy_config_params,
            **kwargs
        }
        
        # Extract strategy_config_params for validation
        if 'strategy_config_params' in config_dict:
            del config_dict['strategy_config_params']
        
        return BacktestConfig(**config_dict)
    
    def run_backtest(
        self,
        backtest_config: BacktestConfig,
        strategy_config_params: Dict[str, Any]
    ) -> BacktestResult:
        """
        Execute backtest with given configuration.
        
        Args:
            backtest_config: Backtest configuration
            strategy_config_params: Strategy-specific parameters
            
        Returns:
            BacktestResult with execution results
        """
        start_time = datetime.now()
        
        try:
            # Build request payload
            request_payload = {
                "data_apikey": self.config.data_api_key,
                "strategy": f"{backtest_config.strategy_name}.py",
                "strategy_config": strategy_config_params,
                "start_date": backtest_config.start_date,
                "end_date": backtest_config.end_date,
                "lookback_minutes": backtest_config.lookback_minutes,
                "capital": backtest_config.initial_capital,
                "leverage": backtest_config.leverage,
                "symbols": backtest_config.symbols,
                "calendar": backtest_config.calendar,
                "frequency": backtest_config.frequency,
                "weight_method": backtest_config.weight_method,
                "generate_pyfolio_report": backtest_config.generate_report
            }
            
            # Add custom weights if specified
            if backtest_config.custom_weights:
                request_payload["custom_weights"] = backtest_config.custom_weights
            
            self.logger.info(f"Starting backtest for {backtest_config.strategy_name}")
            self.logger.debug(f"Request payload: {json.dumps(request_payload, indent=2)}")
            
            # Execute backtest
            response = self.api_client.run_backtest(request_payload)
            
            if not response.success:
                return BacktestResult(
                    success=False,
                    strategy_name=backtest_config.strategy_name,
                    execution_time=start_time,
                    report_type="error",
                    logs="",
                    error_message=response.error_message
                )
            
            # Process results
            result_data = response.data
            report_type = result_data.get('report_type', 'unknown')
            
            # Create result object
            result = BacktestResult(
                success=True,
                strategy_name=backtest_config.strategy_name,
                execution_time=start_time,
                report_type=report_type,
                logs=result_data.get('logs', ''),
                stdout=result_data.get('stdout', '')
            )
            
            # Handle HTML report if present
            if report_type == 'html' and result_data.get('html_content'):
                result.html_content = result_data['html_content']
                result.html_file_path = self._save_html_report(
                    result.html_content,
                    backtest_config.strategy_name,
                    start_time
                )
            
            self.logger.info(f"Backtest completed successfully for {backtest_config.strategy_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Backtest execution failed: {e}")
            return BacktestResult(
                success=False,
                strategy_name=backtest_config.strategy_name,
                execution_time=start_time,
                report_type="error",
                logs="",
                error_message=str(e)
            )
    
    def _save_html_report(self, html_content: str, strategy_name: str, timestamp: datetime) -> str:
        """
        Save HTML report to file.
        
        Args:
            html_content: HTML content to save
            strategy_name: Name of the strategy
            timestamp: Execution timestamp
            
        Returns:
            Path to saved file
        """
        filename = f"{timestamp.strftime('%Y-%m-%d_%H-%M')}_{strategy_name}_backtest_report.html"
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report saved: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save HTML report: {e}")
            return ""
    
    def run_complete_backtest(
        self,
        strategy_name: str,
        strategy_config_params: Dict[str, Any],
        trade_type: str = "future",
        **backtest_params
    ) -> BacktestResult:
        """
        Run complete backtest workflow: upload strategy, configure, and execute.
        
        Args:
            strategy_name: Name of the strategy
            strategy_config_params: Strategy-specific parameters
            trade_type: 'future' or 'spot'
            **backtest_params: Additional backtest parameters
            
        Returns:
            BacktestResult with execution results
        """
        # Step 1: Upload strategy
        strategy_key = f"{trade_type}.{strategy_name}"
        
        if strategy_key not in self._uploaded_strategies:
            self.logger.info(f"Uploading strategy: {strategy_name}")
            upload_response = self.upload_strategy(strategy_name, trade_type)
            
            if not upload_response.success:
                return BacktestResult(
                    success=False,
                    strategy_name=strategy_name,
                    execution_time=datetime.now(),
                    report_type="error",
                    logs="",
                    error_message=f"Strategy upload failed: {upload_response.error_message}"
                )
        
        # Step 2: Create backtest configuration
        backtest_config = self.create_backtest_config(
            strategy_name=strategy_name,
            strategy_config_params=strategy_config_params,
            trade_type=trade_type,
            **backtest_params
        )
        
        # Step 3: Execute backtest
        return self.run_backtest(backtest_config, strategy_config_params)
    
    def get_strategy_config_template(self, strategy_name: str, trade_type: str = "future") -> Dict[str, Any]:
        """
        Get strategy configuration template.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            
        Returns:
            Strategy configuration template
        """
        try:
            config = self.strategy_manager.load_strategy_config(strategy_name, trade_type)
            return config
        except Exception as e:
            self.logger.error(f"Failed to load strategy config template: {e}")
            return {
                "strategy_config": {},
                "rebalancing_config": {
                    "rebalancing_interval_hours": 72,
                    "minimum_candidates": 0
                }
            }
    
    def list_uploaded_strategies(self) -> List[str]:
        """
        Get list of uploaded strategies.
        
        Returns:
            List of uploaded strategy keys
        """
        return list(self._uploaded_strategies.keys())
    
    def clear_uploaded_strategies(self) -> None:
        """Clear the uploaded strategies cache."""
        self._uploaded_strategies.clear()
    
    def print_backtest_result(self, result: BacktestResult) -> None:
        """
        Print backtest result in a formatted way.
        
        Args:
            result: BacktestResult to print
        """
        print(f"\n{'='*60}")
        print(f"🚀 BACKTEST RESULT: {result.strategy_name}")
        print(f"{'='*60}")
        
        if result.success:
            print(f"✅ Status: SUCCESS")
            print(f"📊 Report Type: {result.report_type}")
            print(f"⏰ Execution Time: {result.execution_time}")
            
            if result.html_file_path:
                print(f"📄 HTML Report: {result.html_file_path}")
            
            if result.logs:
                print(f"\n📋 Execution Logs:")
                print("-" * 40)
                print(result.logs)
            
            if result.stdout:
                print(f"\n🖥️ Output:")
                print("-" * 40)
                print(result.stdout)
        else:
            print(f"❌ Status: FAILED")
            print(f"⚠️ Error: {result.error_message}")
        
        print(f"{'='*60}")
    
    def __str__(self) -> str:
        """String representation of BacktestRunner."""
        return f"BacktestRunner(output_dir={self.output_dir}, strategies={len(self._uploaded_strategies)})" 