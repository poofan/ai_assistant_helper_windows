"""
Automation Service for clicking on UI elements using saved coordinates
"""

import pyautogui
import time
import logging
from typing import Dict, List, Optional, Tuple
from .coordinates_manager import CoordinatesManager

class AutomationService:
    """Service for automating UI interactions using saved coordinates"""
    
    def __init__(self, coordinates_manager: CoordinatesManager):
        self.coordinates_manager = coordinates_manager
        self.logger = logging.getLogger(__name__)
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True  # Move mouse to corner to stop
        pyautogui.PAUSE = 0.1  # Small pause between actions
    
    def click_element(self, element_name: str, button: str = 'left', clicks: int = 1, interval: float = 0.0) -> bool:
        """Click on an element by name"""
        try:
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
    
    def double_click_element(self, element_name: str) -> bool:
        """Double click on an element"""
        return self.click_element(element_name, clicks=2, interval=0.1)
    
    def right_click_element(self, element_name: str) -> bool:
        """Right click on an element"""
        return self.click_element(element_name, button='right')
    
    def hover_element(self, element_name: str) -> bool:
        """Hover over an element without clicking"""
        try:
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
    
    def get_element_center(self, element_name: str) -> Optional[Tuple[int, int]]:
        """Get center coordinates of an element"""
        return self.coordinates_manager.get_element_center(element_name)
    
    def is_element_available(self, element_name: str) -> bool:
        """Check if element coordinates are available"""
        coords = self.coordinates_manager.get_coordinates(element_name)
        return coords is not None and len(coords) == 4
    
    def get_available_elements(self) -> List[str]:
        """Get list of available elements"""
        return self.coordinates_manager.get_available_elements()
    
    def perform_poker_action(self, action: str) -> bool:
        """Perform a specific poker action"""
        try:
            action_map = {
                'fold': 'button_fold',
                'call': 'button_call', 
                'raise': 'button_raise',
                'check': 'button_check'
            }
            
            element_name = action_map.get(action.lower())
            if not element_name:
                self.logger.error(f"Unknown poker action: {action}")
                return False
            
            if not self.is_element_available(element_name):
                self.logger.error(f"Element {element_name} not available")
                return False
            
            self.logger.info(f"Performing poker action: {action}")
            return self.click_element(element_name)
            
        except Exception as e:
            self.logger.error(f"Error performing poker action {action}: {e}")
            return False
    
    def get_player_balance(self) -> Optional[str]:
        """Get player balance (would need OCR or other method)"""
        # This is a placeholder - in real implementation you'd use OCR
        # to read the balance from the screen
        self.logger.info("Getting player balance (placeholder)")
        return "1000"  # Placeholder
    
    def get_table_cards(self) -> Optional[str]:
        """Get table cards (would need OCR or other method)"""
        # This is a placeholder - in real implementation you'd use OCR
        # to read the cards from the screen
        self.logger.info("Getting table cards (placeholder)")
        return "A♠ K♥"  # Placeholder
    
    def wait_for_element(self, element_name: str, timeout: float = 5.0) -> bool:
        """Wait for an element to be available (placeholder)"""
        # This is a placeholder - in real implementation you'd check
        # if the element is visible/clickable
        self.logger.info(f"Waiting for element {element_name} (placeholder)")
        time.sleep(0.5)  # Placeholder delay
        return True
    
    def take_screenshot_of_element(self, element_name: str, save_path: str) -> bool:
        """Take screenshot of a specific element"""
        try:
            coords = self.coordinates_manager.get_coordinates(element_name)
            if not coords:
                self.logger.error(f"Coordinates not found for element: {element_name}")
                return False
            
            x, y, width, height = coords
            
            # Take screenshot of the element area
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save(save_path)
            
            self.logger.info(f"Screenshot of {element_name} saved to {save_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error taking screenshot of element {element_name}: {e}")
            return False
