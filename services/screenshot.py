"""
Screenshot Service - Handles screenshot capture and application detection
"""

import mss
import psutil
import win32gui
import win32process
import win32con
from PIL import Image
import logging
from pathlib import Path
from typing import List, Dict, Optional
import time

class ScreenshotService:
    """Service for capturing screenshots and managing applications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Initialize MSS for fast screenshots
        self.mss_instance = mss.mss()
    
    def capture_full_screen(self) -> Optional[str]:
        """Capture full screen screenshot"""
        try:
            # Get primary monitor
            monitor = self.mss_instance.monitors[1]  # 0 is all monitors, 1 is primary
            
            # Capture screenshot
            screenshot = self.mss_instance.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Save to file
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            img.save(filepath)
            self.logger.info(f"Full screen screenshot saved: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Full screen capture failed: {e}")
            return None
    
    def capture_application(self, pid: int, hwnd: Optional[int] = None) -> Optional[str]:
        """Capture screenshot of specific application window"""
        try:
            # Use provided handle or find window handle from PID
            if not hwnd:
                hwnd = self.get_window_handle_from_pid(pid)
                if not hwnd:
                    self.logger.error(f"No window found for PID {pid}")
                    return None
            
            # Check if window is minimized
            was_minimized = win32gui.IsIconic(hwnd)
            self.logger.info(f"Window for PID {pid} is {'minimized' if was_minimized else 'visible'}")
            
            # For minimized windows, we need to use PrintWindow API directly
            if was_minimized:
                self.logger.info(f"Capturing minimized window for PID {pid} using PrintWindow API...")
                screenshot_path = self._capture_minimized_window(hwnd, pid)
                if screenshot_path and self._is_valid_image(screenshot_path):
                    self.logger.info(f"Minimized window screenshot saved: {screenshot_path}")
                    return screenshot_path
                else:
                    self.logger.warning(f"Failed to capture minimized window, trying restore method...")
            
            # For visible windows or if minimized capture failed, restore temporarily
            if was_minimized:
                self.logger.info(f"Restoring window for PID {pid} temporarily...")
                # Restore window
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Bring to front
                win32gui.SetForegroundWindow(hwnd)
                # Wait a bit for window to restore
                time.sleep(0.5)
            
            # HIDE ALL OTHER WINDOWS FOR CLEAN SCREENSHOT
            self.logger.info(f"Hiding all windows except target (PID {pid}) for clean screenshot...")
            hidden_windows = self._hide_all_windows_except(hwnd)
            
            try:
                # Get window rectangle
                rect = win32gui.GetWindowRect(hwnd)
                x, y, right, bottom = rect
                width = right - x
                height = bottom - y
                
                self.logger.info(f"Window dimensions: {width}x{height} at ({x}, {y})")
                
                if width <= 0 or height <= 0:
                    self.logger.error(f"Invalid window dimensions: {width}x{height}")
                    return None
                
                # Try multiple capture methods - PrintWindow is the most reliable for window content
                screenshot_path = None
                
                # Method 1: Try PrintWindow API first (captures actual window content)
                try:
                    screenshot_path = self._capture_with_printwindow(hwnd, width, height, pid)
                    if screenshot_path and self._is_valid_image(screenshot_path):
                        self.logger.info(f"Application screenshot saved with PrintWindow: {screenshot_path}")
                        return screenshot_path
                    else:
                        self.logger.warning(f"PrintWindow method failed or returned invalid image")
                except Exception as e:
                    self.logger.debug(f"PrintWindow method failed: {e}")
                
                # Method 1.5: Try BitBlt method (alternative window content capture)
                try:
                    screenshot_path = self._capture_with_bitblt(hwnd, width, height, pid)
                    if screenshot_path and self._is_valid_image(screenshot_path):
                        self.logger.info(f"Application screenshot saved with BitBlt: {screenshot_path}")
                        return screenshot_path
                    else:
                        self.logger.warning(f"BitBlt method failed or returned invalid image")
                except Exception as e:
                    self.logger.debug(f"BitBlt method failed: {e}")
                
                # Method 1.6: Try GetDIBits method (advanced window content capture)
                try:
                    screenshot_path = self._capture_with_getdibits(hwnd, width, height, pid)
                    if screenshot_path and self._is_valid_image(screenshot_path):
                        self.logger.info(f"Application screenshot saved with GetDIBits: {screenshot_path}")
                        return screenshot_path
                    else:
                        self.logger.warning(f"GetDIBits method failed or returned invalid image")
                except Exception as e:
                    self.logger.debug(f"GetDIBits method failed: {e}")
                
                # Method 2: Try alternative PrintWindow with different dimensions
                try:
                    # Try with client area dimensions
                    client_rect = win32gui.GetClientRect(hwnd)
                    client_width = client_rect[2] - client_rect[0]
                    client_height = client_rect[3] - client_rect[1]
                    if client_width > 0 and client_height > 0:
                        screenshot_path = self._capture_with_printwindow(hwnd, client_width, client_height, pid)
                        if screenshot_path and self._is_valid_image(screenshot_path):
                            self.logger.info(f"Application screenshot saved with PrintWindow (client area): {screenshot_path}")
                            return screenshot_path
                except Exception as e:
                    self.logger.debug(f"PrintWindow client area method failed: {e}")
                
                # Method 3: Try MSS with client area (only as fallback)
                try:
                    screenshot_path = self._capture_with_mss_client(hwnd, width, height, pid)
                    if screenshot_path and self._is_valid_image(screenshot_path):
                        self.logger.info(f"Application screenshot saved with MSS client: {screenshot_path}")
                        return screenshot_path
                except Exception as e:
                    self.logger.debug(f"MSS client method failed: {e}")
                
                # Method 4: Try MSS with window coordinates (last resort - captures screen area)
                try:
                    screenshot_path = self._capture_with_mss_window(hwnd, x, y, width, height, pid)
                    if screenshot_path and self._is_valid_image(screenshot_path):
                        self.logger.warning(f"Application screenshot saved with MSS (screen area): {screenshot_path}")
                        return screenshot_path
                except Exception as e:
                    self.logger.debug(f"MSS window method failed: {e}")
                
                self.logger.error(f"All capture methods failed for PID {pid}")
                return None
                
            finally:
                # ALWAYS RESTORE HIDDEN WINDOWS
                self.logger.info(f"Restoring {len(hidden_windows)} hidden windows...")
                self._restore_windows(hidden_windows)
                
                # Restore minimized state if it was minimized
                if was_minimized:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            
        except Exception as e:
            self.logger.error(f"Application capture failed for PID {pid}: {e}")
            return None
    
    def _capture_minimized_window(self, hwnd: int, pid: int) -> Optional[str]:
        """Capture minimized window using PrintWindow API without restoring"""
        try:
            import win32ui
            import win32con
            import win32api
            
            # Get window dimensions from window placement
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                # Get the normal window rectangle (not minimized)
                rect = placement[4]  # rcNormalPosition
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
            else:
                # Fallback to GetWindowRect
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
            
            if width <= 0 or height <= 0:
                self.logger.error(f"Invalid minimized window dimensions: {width}x{height}")
                return None
            
            self.logger.info(f"Capturing minimized window with dimensions: {width}x{height}")
            
            # Get device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Print window to bitmap using win32api
            PW_RENDERFULLCONTENT = 3
            result = win32api.PrintWindow(hwnd, saveDC.GetSafeHdc(), PW_RENDERFULLCONTENT)
        
            if result:
                # Save bitmap
                timestamp = int(time.time())
                filename = f"minimized_app_screenshot_{pid}_{timestamp}.png"
                filepath = self.screenshots_dir / filename
                saveBitMap.SaveBitmapFile(saveDC, str(filepath))
                
                # Cleanup
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                return str(filepath)
            
            # Cleanup on failure
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Minimized window capture failed: {e}")
            return None
    
    def _capture_with_getdibits(self, hwnd: int, width: int, height: int, pid: int) -> Optional[str]:
        """Capture window using GetDIBits API"""
        try:
            import win32ui
            import win32con
            import win32api
            import struct
            
            self.logger.info(f"Attempting GetDIBits capture for PID {pid} with dimensions {width}x{height}")
            
            # Get device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Get bitmap info
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            # Create PIL image from bitmap data
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Save image
            timestamp = int(time.time())
            filename = f"getdibits_app_screenshot_{pid}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            img.save(filepath)
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            # Verify the image is not empty/black
            if self._is_valid_image(str(filepath)):
                self.logger.info(f"GetDIBits capture successful: {filepath}")
                return str(filepath)
            else:
                self.logger.warning(f"GetDIBits capture resulted in invalid/empty image: {filepath}")
                return None
            
        except Exception as e:
            self.logger.debug(f"GetDIBits method failed: {e}")
            return None
    
    def _capture_with_bitblt(self, hwnd: int, width: int, height: int, pid: int) -> Optional[str]:
        """Capture window using BitBlt API"""
        try:
            import win32ui
            import win32con
            import win32api
            
            self.logger.info(f"Attempting BitBlt capture for PID {pid} with dimensions {width}x{height}")
            
            # Get device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Use BitBlt to copy window content
            result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            
            if result:
                # Save bitmap
                timestamp = int(time.time())
                filename = f"bitblt_app_screenshot_{pid}_{timestamp}.png"
                filepath = self.screenshots_dir / filename
                saveBitMap.SaveBitmapFile(saveDC, str(filepath))
                
                # Cleanup
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                # Verify the image is not empty/black
                if self._is_valid_image(str(filepath)):
                    self.logger.info(f"BitBlt capture successful: {filepath}")
                    return str(filepath)
                else:
                    self.logger.warning(f"BitBlt capture resulted in invalid/empty image: {filepath}")
                    return None
            
            # Cleanup on failure
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"BitBlt method failed: {e}")
            return None
    
    def _capture_with_printwindow(self, hwnd: int, width: int, height: int, pid: int) -> Optional[str]:
        """Capture window using PrintWindow API"""
        try:
            import win32ui
            import win32con
            import win32api
            
            self.logger.info(f"Attempting PrintWindow capture for PID {pid} with dimensions {width}x{height}")
            
            # Get device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Print window to bitmap using win32api
            # Try different PrintWindow flags for better compatibility
            flags_to_try = [
                3,  # PW_RENDERFULLCONTENT
                2,  # PW_CLIENTONLY
                1,  # PW_PRINTCLIENT
                0   # Default
            ]
            
            result = False
            for flag in flags_to_try:
                try:
                    result = win32api.PrintWindow(hwnd, saveDC.GetSafeHdc(), flag)
                    if result:
                        self.logger.debug(f"PrintWindow succeeded with flag {flag}")
                        break
                except Exception as e:
                    self.logger.debug(f"PrintWindow with flag {flag} failed: {e}")
                    continue
        
            if result:
                # Save bitmap
                timestamp = int(time.time())
                filename = f"app_screenshot_{pid}_{timestamp}.png"
                filepath = self.screenshots_dir / filename
                saveBitMap.SaveBitmapFile(saveDC, str(filepath))
                
                # Cleanup
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
                
                # Verify the image is not empty/black
                if self._is_valid_image(str(filepath)):
                    self.logger.info(f"PrintWindow capture successful: {filepath}")
                    return str(filepath)
                else:
                    self.logger.warning(f"PrintWindow capture resulted in invalid/empty image: {filepath}")
                    return None
            
            # Cleanup on failure
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"PrintWindow method failed: {e}")
            return None
    
    def _capture_with_mss_window(self, hwnd: int, x: int, y: int, width: int, height: int, pid: int) -> Optional[str]:
        """Capture window using MSS with window coordinates"""
        # Capture window area
        monitor = {
            "top": y,
            "left": x,
            "width": width,
            "height": height
        }
        
        screenshot = self.mss_instance.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # Save to file
        timestamp = int(time.time())
        filename = f"app_screenshot_{pid}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        img.save(filepath)
        return str(filepath)
    
    def _capture_with_mss_client(self, hwnd: int, width: int, height: int, pid: int) -> Optional[str]:
        """Capture window using MSS with client area coordinates"""
        # Get client area coordinates
        client_rect = win32gui.GetClientRect(hwnd)
        client_x, client_y = win32gui.ClientToScreen(hwnd, (0, 0))
        client_width = client_rect[2] - client_rect[0]
        client_height = client_rect[3] - client_rect[1]
        
        if client_width <= 0 or client_height <= 0:
            return None
        
        # Capture client area
        monitor = {
            "top": client_y,
            "left": client_x,
            "width": client_width,
            "height": client_height
        }
        
        screenshot = self.mss_instance.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        # Save to file
        timestamp = int(time.time())
        filename = f"app_screenshot_{pid}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        img.save(filepath)
        return str(filepath)
    
    def _hide_all_windows_except(self, target_hwnd: int) -> List[int]:
        """Hide all visible windows except the target window"""
        hidden_windows = []
        try:
            def enum_windows_callback(hwnd, windows):
                # Skip the target window
                if hwnd == target_hwnd:
                    return True
                
                # Check if window is visible
                if win32gui.IsWindowVisible(hwnd):
                    # Get window title to avoid hiding system windows
                    title = win32gui.GetWindowText(hwnd)
                    if title and not title.startswith(('Program Manager', 'Desktop', 'Start')):
                        try:
                            # Hide the window
                            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                            windows.append(hwnd)
                            self.logger.debug(f"Hidden window: {title} (HWND: {hwnd})")
                        except Exception as e:
                            self.logger.debug(f"Failed to hide window {hwnd}: {e}")
                
                return True
            
            # Enumerate and hide all windows
            win32gui.EnumWindows(enum_windows_callback, hidden_windows)
            self.logger.info(f"Hidden {len(hidden_windows)} windows for clean screenshot")
            return hidden_windows
            
        except Exception as e:
            self.logger.error(f"Error hiding windows: {e}")
            return []
    
    def _restore_windows(self, hidden_windows: List[int]):
        """Restore previously hidden windows"""
        try:
            for hwnd in hidden_windows:
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    self.logger.debug(f"Restored window: HWND {hwnd}")
                except Exception as e:
                    self.logger.debug(f"Failed to restore window {hwnd}: {e}")
            
            self.logger.info(f"Restored {len(hidden_windows)} windows")
            
        except Exception as e:
            self.logger.error(f"Error restoring windows: {e}")
    
    def _is_valid_image(self, filepath: str) -> bool:
        """Check if image is valid (not black/empty)"""
        try:
            img = Image.open(filepath)
            width, height = img.size
            
            # Check if image has reasonable dimensions
            if width < 10 or height < 10:
                self.logger.debug(f"Image too small: {width}x{height}")
                return False
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Check if image is not completely black or white
            pixels = list(img.getdata())
            if len(pixels) == 0:
                self.logger.debug("No pixels in image")
                return False
            
            # Sample pixels from different areas of the image
            sample_size = min(1000, len(pixels))
            sample_pixels = pixels[::max(1, len(pixels) // sample_size)]
            
            # Count non-black and non-white pixels
            non_black_pixels = sum(1 for pixel in sample_pixels if pixel != (0, 0, 0))
            non_white_pixels = sum(1 for pixel in sample_pixels if pixel != (255, 255, 255))
            
            # Image should have at least 5% non-black and non-white pixels
            min_content_pixels = max(10, len(sample_pixels) * 0.05)
            
            is_valid = non_black_pixels >= min_content_pixels and non_white_pixels >= min_content_pixels
            
            if not is_valid:
                self.logger.debug(f"Image appears to be mostly black/white: {non_black_pixels}/{len(sample_pixels)} non-black, {non_white_pixels}/{len(sample_pixels)} non-white")
            
            return is_valid
            
        except Exception as e:
            self.logger.debug(f"Error validating image {filepath}: {e}")
            return False
    
    def get_running_applications(self) -> List[Dict]:
        """Get list of running applications with visible and minimized windows"""
        applications = []
        
        try:
            def enum_windows_callback(hwnd, windows):
                # Check if window has a title (not empty)
                title = win32gui.GetWindowText(hwnd)
                if not title or title.startswith(('Program Manager', 'Desktop', 'Start')):
                    return
                
                # Check if window is visible OR minimized (but not hidden)
                is_visible = win32gui.IsWindowVisible(hwnd)
                is_minimized = win32gui.IsIconic(hwnd)
                
                # Include visible windows and minimized windows (but not completely hidden)
                if is_visible or is_minimized:
                    # Get process ID
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        
                        # Get process name
                        try:
                            process = psutil.Process(pid)
                            process_name = process.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            process_name = "Unknown"
                        
                        # Determine window state
                        window_state = "visible" if is_visible else "minimized"
                        
                        # Check if we already have this process
                        existing = next((app for app in windows if app['pid'] == pid), None)
                        if not existing:
                            windows.append({
                                'pid': pid,
                                'name': process_name,
                                'title': title,
                                'hwnd': hwnd,
                                'state': window_state
                            })
                        else:
                            # Update title and state if this window has a more descriptive title or better state
                            if len(title) > len(existing['title']) or (existing['state'] == 'minimized' and window_state == 'visible'):
                                existing['title'] = title
                                existing['state'] = window_state
                                
                    except Exception as e:
                        self.logger.debug(f"Error getting process info for window {hwnd}: {e}")
                
                return True
            
            # Enumerate all windows
            win32gui.EnumWindows(enum_windows_callback, applications)
            
            # Sort by process name
            applications.sort(key=lambda x: x['name'].lower())
            
            self.logger.info(f"Found {len(applications)} running applications")
            return applications
            
        except Exception as e:
            self.logger.error(f"Error getting running applications: {e}")
            return []
    
    def get_window_handle_from_pid(self, pid: int) -> Optional[int]:
        """Get window handle from process ID"""
        hwnd = None
        
        def enum_windows_callback(window_hwnd, param):
            nonlocal hwnd
            try:
                # Check if window is valid
                if not win32gui.IsWindow(window_hwnd):
                    return True
                
                # Get window thread process ID
                _, window_pid = win32process.GetWindowThreadProcessId(window_hwnd)
                if window_pid == pid:
                    # Check if window has a title
                    title = win32gui.GetWindowText(window_hwnd)
                    if title:  # Only consider windows with titles
                        # Check if window is visible OR minimized
                        is_visible = win32gui.IsWindowVisible(window_hwnd)
                        is_minimized = win32gui.IsIconic(window_hwnd)
                        
                        if is_visible or is_minimized:
                            hwnd = window_hwnd
                            return False  # Stop enumeration
            except Exception as e:
                # Log debug info but continue enumeration
                self.logger.debug(f"Error in enum callback for hwnd {window_hwnd}: {e}")
                pass
            return True  # Continue enumeration
        
        try:
            win32gui.EnumWindows(enum_windows_callback, None)
            return hwnd
        except Exception as e:
            self.logger.error(f"Error finding window for PID {pid}: {e}")
            return None
    
    def get_window_info(self, hwnd: int) -> Dict:
        """Get detailed information about a window"""
        try:
            title = win32gui.GetWindowText(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            return {
                'hwnd': hwnd,
                'title': title,
                'rect': rect,
                'pid': pid,
                'visible': win32gui.IsWindowVisible(hwnd)
            }
        except Exception as e:
            self.logger.error(f"Error getting window info for {hwnd}: {e}")
            return {}
    
    def cleanup_old_screenshots(self, max_age_hours: int = 24):
        """Clean up old screenshot files"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.screenshots_dir.glob("*.png"):
                if current_time - file_path.stat().st_mtime > max_age_seconds:
                    file_path.unlink()
                    self.logger.info(f"Deleted old screenshot: {file_path}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up screenshots: {e}")

