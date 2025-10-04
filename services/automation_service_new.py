"""
Flexible Automation Service for clicking on UI elements using saved coordinates
"""

import pyautogui
import time
import logging
from typing import Dict, List, Optional, Tuple
from .coordinates_manager import CoordinatesManager

class AutomationService:
    """Service for automating UI interactions using flexible button system"""
    
    def __init__(self, coordinates_manager: CoordinatesManager):
        self.coordinates_manager = coordinates_manager
        self.logger = logging.getLogger(__name__)
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True  # Move mouse to corner to stop
        pyautogui.PAUSE = 0.1  # Small pause between actions
    
    def click_element(self, element_name: str, button: str = 'left', clicks: int = 1, interval: float = 0.0) -> bool:
        """Legacy method - click on an element by name (for info elements)"""
        try:
            # Try to get coordinates from info_elements first
            info_elements = self.coordinates_manager.get_all_info_elements()
            if element_name in info_elements:
                coords = info_elements[element_name].get("coordinates")
            else:
                # Fallback to old format
                coords = self.coordinates_manager.get_coordinates(element_name)
            
            if not coords:
                self.logger.error(f"Coordinates not found for element: {element_name}")
                return False
            
            x, y, width, height = coords
            center_x = x + width // 2
            center_y = y + height // 2
            
            self.logger.info(f"Clicking {element_name} at ({center_x}, {center_y})")
            
            # Move to element center and click
            pyautogui.moveTo(center_x, center_y)
            pyautogui.click(center_x, center_y, button=button, clicks=clicks, interval=interval)
            
            return True
        except Exception as e:
            self.logger.error(f"Error clicking element {element_name}: {e}")
            return False
    
    def click_coordinates(self, x: int, y: int, button: str = 'left', clicks: int = 1, interval: float = 0.0) -> bool:
        """Click at specific coordinates"""
        try:
            self.logger.info(f"Clicking at coordinates ({x}, {y})")
            pyautogui.moveTo(x, y)
            pyautogui.click(x, y, button=button, clicks=clicks, interval=interval)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking at coordinates ({x}, {y}): {e}")
            return False
    
    def perform_button_action(self, button_id: str) -> bool:
        """Perform a button click by button ID"""
        try:
            # Check if button exists in coordinates
            if not self.coordinates_manager.get_button_coordinates(button_id):
                available_buttons = self.coordinates_manager.get_available_button_ids()
                self.logger.error(f"Button '{button_id}' not found in coordinates. Available buttons: {available_buttons}")
                return False
            
            # Get button center coordinates
            center = self.coordinates_manager.get_button_center(button_id)
            if not center:
                self.logger.error(f"Could not get center coordinates for button: {button_id}")
                return False
            
            center_x, center_y = center
            button_info = self.coordinates_manager.get_button_info(button_id)
            button_name = button_info.get("name", button_id) if button_info else button_id
            
            self.logger.info(f"Clicking button '{button_name}' ({button_id}) at ({center_x}, {center_y})")
            
            # Move to button center and click
            pyautogui.moveTo(center_x, center_y)
            pyautogui.click(center_x, center_y)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing button action {button_id}: {e}")
            return False
    
    # Legacy method for backward compatibility
    def perform_poker_action(self, action: str) -> bool:
        """Legacy method - maps old poker actions to new button system"""
        try:
            action_map = {
                'fold': 'fold',
                'call': 'call', 
                'raise': 'raise',
                'check': 'check'
            }
            
            button_id = action_map.get(action.lower())
            if not button_id:
                self.logger.error(f"Unknown poker action: {action}")
                return False
            
            return self.perform_button_action(button_id)
            
        except Exception as e:
            self.logger.error(f"Error performing poker action {action}: {e}")
            return False
    
    def double_click_element(self, element_name: str) -> bool:
        """Double click on an element"""
        return self.click_element(element_name, clicks=2, interval=0.1)
    
    def right_click_element(self, element_name: str) -> bool:
        """Right click on an element"""
        return self.click_element(element_name, button='right')
    
    def hover_element(self, element_name: str) -> bool:
        """Hover over an element without clicking"""
        try:
            # Try to get coordinates from info_elements first
            info_elements = self.coordinates_manager.get_all_info_elements()
            if element_name in info_elements:
                coords = info_elements[element_name].get("coordinates")
            else:
                # Fallback to old format
                coords = self.coordinates_manager.get_coordinates(element_name)
            
            if not coords:
                self.logger.error(f"Coordinates not found for element: {element_name}")
                return False
            
            x, y, width, height = coords
            center_x = x + width // 2
            center_y = y + height // 2
            
            self.logger.info(f"Hovering over {element_name} at ({center_x}, {center_y})")
            pyautogui.moveTo(center_x, center_y)
            return True
        except Exception as e:
            self.logger.error(f"Error hovering over element {element_name}: {e}")
            return False
    
    def is_element_available(self, element_name: str) -> bool:
        """Check if element coordinates are available"""
        try:
            # Check info elements first
            info_elements = self.coordinates_manager.get_all_info_elements()
            if element_name in info_elements:
                return True
            
            # Check buttons
            if element_name in self.coordinates_manager.get_all_buttons():
                return True
            
            # Fallback to old method
            coords = self.coordinates_manager.get_coordinates(element_name)
            return coords is not None
        except Exception as e:
            self.logger.error(f"Error checking element availability {element_name}: {e}")
            return False
    
    def get_available_elements(self) -> List[str]:
        """Get list of all available elements"""
        try:
            elements = []
            
            # Add info elements
            info_elements = self.coordinates_manager.get_all_info_elements()
            elements.extend(info_elements.keys())
            
            # Add buttons
            buttons = self.coordinates_manager.get_all_buttons()
            elements.extend(buttons.keys())
            
            return elements
        except Exception as e:
            self.logger.error(f"Error getting available elements: {e}")
            return []
    
    def get_available_buttons(self) -> List[str]:
        """Get list of available button IDs"""
        return self.coordinates_manager.get_available_button_ids()


