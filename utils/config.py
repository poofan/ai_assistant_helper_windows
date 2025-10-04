"""
Configuration management for the AI Chat Messenger
"""

import configparser
import json
import logging
import sys
import os
from pathlib import Path
from typing import Any, Optional

class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.logger = logging.getLogger(__name__)
        
        # Handle PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            base_path = sys._MEIPASS
            self.config_file = Path(base_path) / config_file
        else:
            # Running as Python script
            self.config_file = Path(config_file)
        
        self.config = configparser.ConfigParser()
        
        # Default configuration
        self.defaults = {
            'api': {
                'base_url': 'http://147.45.227.57',
                'timeout': '30',
                'retry_attempts': '3'
            },
            'gui': {
                'theme': 'default',
                'font_size': '10',
                'window_width': '1000',
                'window_height': '700',
                'sidebar_visible': 'true'
            },
            'screenshots': {
                'save_directory': 'screenshots',
                'max_age_hours': '24',
                'format': 'png',
                'quality': '95'
            },
            'logging': {
                'level': 'INFO',
                'max_file_size': '10485760',  # 10MB
                'backup_count': '5'
            }
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file, encoding='utf-8')
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.create_default_config()
                self.logger.info(f"Default configuration created at {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        try:
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Set default values
            for section, options in self.defaults.items():
                self.config.add_section(section)
                for key, value in options.items():
                    self.config.set(section, key, value)
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
                
        except Exception as e:
            self.logger.error(f"Error creating default configuration: {e}")
    
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get configuration value as integer"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get configuration value as float"""
        try:
            return self.config.getfloat(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get configuration value as boolean"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, key, str(value))
            self.save_config()
            
        except Exception as e:
            self.logger.error(f"Error setting configuration {section}.{key}: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get_section(self, section: str) -> dict:
        """Get entire configuration section as dictionary"""
        try:
            if self.config.has_section(section):
                return dict(self.config.items(section))
            return {}
        except Exception as e:
            self.logger.error(f"Error getting section {section}: {e}")
            return {}
    
    def has_section(self, section: str) -> bool:
        """Check if configuration section exists"""
        return self.config.has_section(section)
    
    def has_option(self, section: str, key: str) -> bool:
        """Check if configuration option exists"""
        return self.config.has_option(section, key)

