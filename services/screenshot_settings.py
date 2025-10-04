"""
Screenshot Settings Service - Manages screenshot preferences
"""

import json
import logging
import sys
import os
from pathlib import Path

class ScreenshotSettingsService:
    """Service for managing screenshot settings"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Handle PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle - use executable directory
            base_path = os.path.dirname(sys.executable)
            self.settings_file = Path(base_path) / "data/screenshot_settings.json"
        else:
            # Running as Python script
            self.settings_file = Path("data/screenshot_settings.json")
        
        self.settings_file.parent.mkdir(exist_ok=True)
        
        # Default settings
        self.default_settings = {
            "screenshot_type": "fullscreen",
            "prompt": "Проанализируй этот скриншот максимально подробно на русском языке. Опиши все элементы интерфейса, текст, изображения, цвета, расположение элементов, функциональные кнопки, меню, статусы, ошибки, предупреждения, и любые другие детали. Если это веб-страница - укажи URL, заголовок, содержимое. Если это приложение - опиши его функциональность и текущее состояние. Будь максимально детальным и точным в описании.",
            "selected_app": None,
            "ai_automation_enabled": False,  # Включение автоматизации по ответам ИИ
            "auto_screenshots_interval": 5  # Интервал автоматических скриншотов в секундах
        }
        
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                
                # Migrate settings - add missing default values
                settings_updated = False
                for key, default_value in self.default_settings.items():
                    if key not in self.settings:
                        self.settings[key] = default_value
                        settings_updated = True
                        self.logger.info(f"Added missing setting {key}: {default_value}")
                
                if settings_updated:
                    self.save_settings()
                    self.logger.info("Settings migrated and saved")
                
                self.logger.info("Screenshot settings loaded successfully")
            else:
                self.settings = self.default_settings.copy()
                self.save_settings()
                self.logger.info("Created default screenshot settings")
        except Exception as e:
            self.logger.error(f"Error loading screenshot settings: {e}")
            self.settings = self.default_settings.copy()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            self.logger.info("Screenshot settings saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving screenshot settings: {e}")
    
    def get_settings(self):
        """Get current settings"""
        return self.settings.copy()
    
    def update_settings(self, **kwargs):
        """Update specific settings"""
        for key, value in kwargs.items():
            # Always update the setting, even if it's new
            self.settings[key] = value
            self.logger.info(f"Updated setting {key}: {value}")
        
        self.save_settings()
    
    def reset_settings(self):
        """Reset to default settings"""
        self.settings = self.default_settings.copy()
        self.save_settings()
        self.logger.info("Screenshot settings reset to defaults")

