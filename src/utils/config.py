"""
Configuration Manager
Loads and manages application configuration from YAML file
"""

import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Any, Dict

# Load environment variables
load_dotenv()

class Config:
    """Configuration manager for the trading bot"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._replace_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _replace_env_vars(self):
        """Replace ${VAR_NAME} placeholders with environment variables"""
        def replace_vars(obj):
            if isinstance(obj, dict):
                return {k: replace_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
                var_name = obj[2:-1]
                return os.getenv(var_name, obj)
            return obj
        
        self.config = replace_vars(self.config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'trading.mode')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading configuration"""
        return self.config.get('trading', {})
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration"""
        return self.config.get('data', {})
    
    def get_strategy_config(self) -> Dict[str, Any]:
        """Get strategy configuration"""
        return self.config.get('strategy', {})
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration"""
        return self.config.get('risk', {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.config.get('api', {})
    
    def get_symbols(self) -> list:
        """Get list of trading symbols"""
        trading_config = self.get_trading_config()
        return trading_config.get('symbols', [])


# Global configuration instance
config = Config()
