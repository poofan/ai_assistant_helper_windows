"""
Coordinates Manager for saving and managing UI element coordinates
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class CoordinatesManager:
    """Manages UI element coordinates for automation"""
    
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
    
    def load_coordinates(self) -> Dict[str, List[int]]:
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
    
    def save_coordinates(self, coordinates: Optional[Dict[str, List[int]]] = None) -> bool:
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
    
    def get_coordinates(self, element_name: str) -> Optional[List[int]]:
        """Get coordinates for a specific element"""
        return self.coordinates.get(element_name)
    
    def set_coordinates(self, element_name: str, coordinates: List[int]) -> bool:
        """Set coordinates for a specific element"""
        try:
            if len(coordinates) != 4:
                raise ValueError("Coordinates must be [x, y, width, height]")
            
            self.coordinates[element_name] = coordinates
            self.logger.info(f"Set coordinates for {element_name}: {coordinates}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting coordinates for {element_name}: {e}")
            return False
    
    def update_coordinates(self, updates: Dict[str, List[int]]) -> bool:
        """Update multiple coordinates at once"""
        try:
            for element_name, coordinates in updates.items():
                if len(coordinates) != 4:
                    raise ValueError(f"Coordinates for {element_name} must be [x, y, width, height]")
                self.coordinates[element_name] = coordinates
            
            self.logger.info(f"Updated coordinates: {list(updates.keys())}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating coordinates: {e}")
            return False
    
    def get_all_coordinates(self) -> Dict[str, List[int]]:
        """Get all coordinates"""
        return self.coordinates.copy()
    
    def reset_to_defaults(self) -> bool:
        """Reset coordinates to default values"""
        try:
            self.coordinates = self.default_coordinates.copy()
            self.save_coordinates()
            self.logger.info("Reset coordinates to defaults")
            return True
        except Exception as e:
            self.logger.error(f"Error resetting coordinates: {e}")
            return False
    
    def get_element_center(self, element_name: str) -> Optional[Tuple[int, int]]:
        """Get center coordinates of an element"""
        coords = self.get_coordinates(element_name)
        if coords:
            x, y, width, height = coords
            center_x = x + width // 2
            center_y = y + height // 2
            return (center_x, center_y)
        return None
    
    def is_coordinates_valid(self, coordinates: List[int]) -> bool:
        """Check if coordinates are valid"""
        return (len(coordinates) == 4 and 
                all(isinstance(coord, int) for coord in coordinates) and
                all(coord >= 0 for coord in coordinates))
    
    def get_available_elements(self) -> List[str]:
        """Get list of available element names"""
        return list(self.coordinates.keys())
