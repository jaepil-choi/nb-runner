"""
API Client for nb-runner

Centralized API communication with retry logic and error handling.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from .config_manager import ConfigManager

@dataclass
class APIResponse:
    """Standardized API response structure."""
    success: bool
    data: Any
    status_code: int
    error_message: Optional[str] = None

class APIClient:
    """
    Centralized API client for nb-runner system.
    
    Handles all API communications with proper error handling and retry logic.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize APIClient.
        
        Args:
            config_manager: ConfigManager instance for API configuration
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Set up session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'nb-runner/1.0.0',
            'Accept': 'application/json'
        })
    
    def _make_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict] = None, 
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        timeout: int = 30
    ) -> APIResponse:
        """
        Make HTTP request with error handling.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            url: Request URL
            data: Form data
            json_data: JSON data
            files: Files to upload
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            APIResponse with success/failure status and data
        """
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                data=data,
                json=json_data,
                files=files,
                params=params,
                timeout=timeout
            )
            
            # Handle response
            if response.status_code >= 400:
                self.logger.error(f"API request failed: {response.status_code} {response.text}")
                return APIResponse(
                    success=False,
                    data=None,
                    status_code=response.status_code,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
            
            return APIResponse(
                success=True,
                data=response_data,
                status_code=response.status_code
            )
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout for {url}")
            return APIResponse(
                success=False,
                data=None,
                status_code=408,
                error_message="Request timeout"
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error for {url}: {e}")
            return APIResponse(
                success=False,
                data=None,
                status_code=500,
                error_message=f"Request error: {str(e)}"
            )
    
    def health_check(self, service: str = 'backtest') -> APIResponse:
        """
        Check API health for specified service.
        
        Args:
            service: Service to check ('backtest', 'trading', 'position')
            
        Returns:
            APIResponse with health status
        """
        url = self.config.get_api_endpoint(service)
        return self._make_request('GET', url)
    
    def upload_strategy(
        self, 
        strategy_file_path: str, 
        strategy_name: str, 
        trade_type: str = 'future',
        service: str = 'backtest'
    ) -> APIResponse:
        """
        Upload strategy file to server.
        
        Args:
            strategy_file_path: Path to strategy file
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            service: 'backtest' or 'trading'
            
        Returns:
            APIResponse with upload status
        """
        base_url = self.config.get_api_endpoint(service)
        
        if service == 'backtest':
            url = f"{base_url}upload/strategy/"
            params = {'tradeType': trade_type}
        else:  # trading
            url = f"{base_url}upload/strategy/"
            params = None
        
        try:
            with open(strategy_file_path, 'rb') as f:
                files = {'file': f}
                return self._make_request('POST', url, files=files, params=params)
        except FileNotFoundError:
            return APIResponse(
                success=False,
                data=None,
                status_code=404,
                error_message=f"Strategy file not found: {strategy_file_path}"
            )
    
    def upload_config(
        self, 
        config_file_path: str, 
        config_name: str,
        service: str = 'trading'
    ) -> APIResponse:
        """
        Upload config file to server.
        
        Args:
            config_file_path: Path to config file
            config_name: Name of the config
            service: 'trading' (configs are only for trading)
            
        Returns:
            APIResponse with upload status
        """
        base_url = self.config.get_api_endpoint(service)
        url = f"{base_url}upload/config/"
        
        try:
            with open(config_file_path, 'rb') as f:
                files = {'file': f}
                return self._make_request('POST', url, files=files)
        except FileNotFoundError:
            return APIResponse(
                success=False,
                data=None,
                status_code=404,
                error_message=f"Config file not found: {config_file_path}"
            )
    
    def check_uploaded_strategy(
        self, 
        strategy_name: str, 
        trade_type: str = 'future',
        service: str = 'backtest'
    ) -> APIResponse:
        """
        Check if strategy file is uploaded.
        
        Args:
            strategy_name: Name of the strategy
            trade_type: 'future' or 'spot'
            service: 'backtest' or 'trading'
            
        Returns:
            APIResponse with strategy info
        """
        base_url = self.config.get_api_endpoint(service)
        
        if service == 'backtest':
            url = f"{base_url}upload/strategy/check/"
            params = {'tradeType': trade_type, 'strategy_name': strategy_name}
        else:  # trading
            url = f"{base_url}upload/check/strategy/"
            params = {'strategy_name': strategy_name}
        
        return self._make_request('GET', url, params=params)
    
    def run_backtest(self, backtest_config: Dict[str, Any]) -> APIResponse:
        """
        Run backtest with given configuration.
        
        Args:
            backtest_config: Backtest configuration dictionary
            
        Returns:
            APIResponse with backtest results
        """
        base_url = self.config.get_api_endpoint('backtest')
        url = f"{base_url}run/future/backtest/"
        
        return self._make_request('POST', url, json_data=backtest_config, timeout=300)
    
    def start_trading(
        self, 
        strategy_name: str, 
        method: str = 'rebalancing'
    ) -> APIResponse:
        """
        Start live trading.
        
        Args:
            strategy_name: Name of the strategy
            method: Trading method ('rebalancing')
            
        Returns:
            APIResponse with session info
        """
        base_url = self.config.get_api_endpoint('trading')
        url = f"{base_url}command/run-system"
        
        data = {
            'strategy_name': strategy_name,
            'method': method
        }
        
        return self._make_request('POST', url, json_data=data)
    
    def terminate_trading(self, session_id: str) -> APIResponse:
        """
        Terminate trading session.
        
        Args:
            session_id: Trading session ID
            
        Returns:
            APIResponse with termination status
        """
        base_url = self.config.get_api_endpoint('trading')
        url = f"{base_url}command/terminate/"
        
        params = {'session_id': session_id}
        
        return self._make_request('GET', url, params=params)
    
    def get_positions(
        self, 
        product_type: str = 'susdt-futures', 
        margin_coin: str = 'susdt'
    ) -> APIResponse:
        """
        Get current positions.
        
        Args:
            product_type: Product type
            margin_coin: Margin coin
            
        Returns:
            APIResponse with position data
        """
        base_url = self.config.get_api_endpoint('position')
        url = f"{base_url}future/position/all-positions"
        
        payload = {
            'user_key': self.config.user_key,
            'all_positions': {
                'productType': product_type,
                'marginCoin': margin_coin.upper()
            }
        }
        
        return self._make_request('POST', url, json_data=payload) 