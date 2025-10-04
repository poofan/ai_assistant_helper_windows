"""
Flexible Coordinates Manager for saving and managing UI element coordinates
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class CoordinatesManager:
    """Manages UI element coordinates for automation with flexible button system"""
    
    def __init__(self, data_dir: str = "data"):
        # Handle PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle - use executable directory
            base_path = os.path.dirname(sys.executable)
            self.data_dir = Path(base_path) / data_dir
        else:
            # Running as Python script
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(exist_ok=True)
        self.coordinates_file = self.data_dir / "coordinates.json"
        self.logger = logging.getLogger(__name__)
        
        # Default coordinates structure - flexible button system
        self.default_coordinates = {
            "buttons": {
                "fold": {
                    "name": "Скинуть",
                    "coordinates": [1400, 800, 110, 55],
                    "description": "Кнопка сброса карт"
                },
                "call": {
                    "name": "Уравнять",
                    "coordinates": [1550, 800, 110, 55],
                    "description": "Кнопка уравнивания ставки"
                },
                "raise": {
                    "name": "Повысить",
                    "coordinates": [1700, 800, 110, 55],
                    "description": "Кнопка повышения ставки"
                },
                "check": {
                    "name": "Пропустить",
                    "coordinates": [1400, 750, 110, 55],
                    "description": "Кнопка пропуска хода"
                }
            },
            "info_elements": {
                "player_cards": {
                    "name": "Карты игрока",
                    "coordinates": [100, 600, 55, 80],
                    "description": "Область карт игрока"
                },
                "player_balance": {
                    "name": "Баланс игрока",
                    "coordinates": [400, 690, 90, 35],
                    "description": "Отображение баланса игрока"
                },
                "table_cards": {
                    "name": "Карты на столе",
                    "coordinates": [500, 300, 55, 80],
                    "description": "Общие карты на столе"
                },
                "bank_total": {
                    "name": "Общий банк",
                    "coordinates": [1100, 250, 80, 35],
                    "description": "Общая сумма в банке"
                }
            }
        }
        
        # Load existing coordinates
        self.coordinates = self.load_coordinates()
    
    def load_coordinates(self) -> Dict:
        """Load coordinates from file"""
        try:
            if self.coordinates_file.exists():
                with open(self.coordinates_file, 'r', encoding='utf-8') as f:
                    coordinates = json.load(f)
                    self.logger.info(f"Loaded coordinates from {self.coordinates_file}")
                    return coordinates
            else:
                # Create default coordinates file
                self.save_coordinates(self.default_coordinates)
                self.logger.info(f"Created default coordinates file at {self.coordinates_file}")
                return self.default_coordinates.copy()
        except Exception as e:
            self.logger.error(f"Error loading coordinates: {e}")
            return self.default_coordinates.copy()
    
    def save_coordinates(self, coordinates: Optional[Dict] = None) -> bool:
        """Save coordinates to file"""
        try:
            if coordinates is None:
                coordinates = self.coordinates
            
            with open(self.coordinates_file, 'w', encoding='utf-8') as f:
                json.dump(coordinates, f, indent=2, ensure_ascii=False)
            
            self.coordinates = coordinates.copy()
            self.logger.info(f"Saved coordinates to {self.coordinates_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving coordinates: {e}")
            return False
    
    def get_button_coordinates(self, button_id: str) -> Optional[List[int]]:
        """Get coordinates for a specific button"""
        try:
            buttons = self.coordinates.get("buttons", {})
            if button_id in buttons:
                return buttons[button_id].get("coordinates")
            return None
        except Exception as e:
            self.logger.error(f"Error getting button coordinates for {button_id}: {e}")
            return None
    
    def get_button_info(self, button_id: str) -> Optional[Dict]:
        """Get full button information"""
        try:
            buttons = self.coordinates.get("buttons", {})
            if button_id in buttons:
                return buttons[button_id].copy()
            return None
        except Exception as e:
            self.logger.error(f"Error getting button info for {button_id}: {e}")
            return None
    
    def get_all_buttons(self) -> Dict[str, Dict]:
        """Get all available buttons"""
        return self.coordinates.get("buttons", {})
    
    def get_all_info_elements(self) -> Dict[str, Dict]:
        """Get all info elements"""
        return self.coordinates.get("info_elements", {})
    
    def add_button(self, button_id: str, name: str, coordinates: List[int], description: str = "") -> bool:
        """Add a new button"""
        try:
            if "buttons" not in self.coordinates:
                self.coordinates["buttons"] = {}
            
            self.coordinates["buttons"][button_id] = {
                "name": name,
                "coordinates": coordinates,
                "description": description
            }
            
            return self.save_coordinates()
        except Exception as e:
            self.logger.error(f"Error adding button {button_id}: {e}")
            return False
    
    def update_button(self, button_id: str, name: str = None, coordinates: List[int] = None, description: str = None) -> bool:
        """Update an existing button"""
        try:
            if "buttons" not in self.coordinates or button_id not in self.coordinates["buttons"]:
                return False
            
            button = self.coordinates["buttons"][button_id]
            if name is not None:
                button["name"] = name
            if coordinates is not None:
                button["coordinates"] = coordinates
            if description is not None:
                button["description"] = description
            
            return self.save_coordinates()
        except Exception as e:
            self.logger.error(f"Error updating button {button_id}: {e}")
            return False
    
    def remove_button(self, button_id: str) -> bool:
        """Remove a button"""
        try:
            if "buttons" in self.coordinates and button_id in self.coordinates["buttons"]:
                del self.coordinates["buttons"][button_id]
                return self.save_coordinates()
            return False
        except Exception as e:
            self.logger.error(f"Error removing button {button_id}: {e}")
            return False
    
    def get_button_center(self, button_id: str) -> Optional[Tuple[int, int]]:
        """Get center coordinates of a button"""
        try:
            coordinates = self.get_button_coordinates(button_id)
            if coordinates and len(coordinates) >= 4:
                x, y, width, height = coordinates
                center_x = x + width // 2
                center_y = y + height // 2
                return (center_x, center_y)
            return None
        except Exception as e:
            self.logger.error(f"Error getting button center for {button_id}: {e}")
            return None
    
    def validate_coordinates(self, coordinates: List[int]) -> bool:
        """Validate coordinates format"""
        try:
            if not isinstance(coordinates, list) or len(coordinates) != 4:
                return False
            
            x, y, width, height = coordinates
            if not all(isinstance(coord, int) for coord in [x, y, width, height]):
                return False
            
            if width <= 0 or height <= 0:
                return False
            
            return True
        except Exception:
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset coordinates to default values"""
        try:
            self.coordinates = self.default_coordinates.copy()
            return self.save_coordinates()
        except Exception as e:
            self.logger.error(f"Error resetting to defaults: {e}")
            return False
    
    def get_available_button_ids(self) -> List[str]:
        """Get list of available button IDs for automation"""
        return list(self.coordinates.get("buttons", {}).keys())
