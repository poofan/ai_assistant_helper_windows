"""
User Preferences Service - Handles saving and loading user preferences
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

class UserPreferencesService:
    """Service for managing user preferences and saved data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.preferences_file = Path("data") / "user_preferences.json"
        self.preferences_file.parent.mkdir(exist_ok=True)
    
    def save_login_data(self, username: str, password: str, remember_me: bool = True):
        """Save login data if remember_me is True"""
        try:
            if not remember_me:
                # If remember_me is False, remove saved data
                self.clear_login_data()
                return
            
            # Load existing preferences
            preferences = self.load_preferences()
            
            # Update login data
            preferences["login_data"] = {
                "username": username,
                "password": password,
                "remember_me": remember_me
            }
            
            # Save preferences
            self.save_preferences(preferences)
            self.logger.info(f"Login data saved for user: {username}")
            
        except Exception as e:
            self.logger.error(f"Error saving login data: {e}")
    
    def load_login_data(self) -> Optional[Dict[str, str]]:
        """Load saved login data"""
        try:
            preferences = self.load_preferences()
            login_data = preferences.get("login_data", {})
            
            if login_data.get("remember_me", False):
                self.logger.info(f"Login data loaded for user: {login_data.get('username', 'Unknown')}")
                return {
                    "username": login_data.get("username", ""),
                    "password": login_data.get("password", ""),
                    "remember_me": login_data.get("remember_me", False)
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading login data: {e}")
            return None
    
    def clear_login_data(self):
        """Clear saved login data"""
        try:
            preferences = self.load_preferences()
            if "login_data" in preferences:
                del preferences["login_data"]
                self.save_preferences(preferences)
                self.logger.info("Login data cleared")
        except Exception as e:
            self.logger.error(f"Error clearing login data: {e}")
    
    def load_preferences(self) -> Dict:
        """Load all preferences from file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error loading preferences: {e}")
            return {}
    
    def save_preferences(self, preferences: Dict):
        """Save all preferences to file"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving preferences: {e}")
    
    def save_setting(self, key: str, value):
        """Save a specific setting"""
        try:
            preferences = self.load_preferences()
            preferences[key] = value
            self.save_preferences(preferences)
        except Exception as e:
            self.logger.error(f"Error saving setting {key}: {e}")
    
    def load_setting(self, key: str, default=None):
        """Load a specific setting"""
        try:
            preferences = self.load_preferences()
            return preferences.get(key, default)
        except Exception as e:
            self.logger.error(f"Error loading setting {key}: {e}")
            return default
