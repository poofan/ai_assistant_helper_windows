"""
Modern Chat Widget using CustomTkinter for contemporary design
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import logging
import os
from pathlib import Path

from .screenshot_dialog import ScreenshotDialog
from .subscription_dialog import SubscriptionDialog
from services.screenshot_settings import ScreenshotSettingsService
from services.coordinates_manager import CoordinatesManager
from services.automation_service import AutomationService

class ModernChatWidget(ctk.CTkFrame):
    """Modern chat widget using CustomTkinter"""
    
    def __init__(self, parent, api_client, screenshot_service, chat_manager, theme_manager):
        super().__init__(parent)
        
        self.api_client = api_client
        self.screenshot_service = screenshot_service
        self.chat_manager = chat_manager
        self.theme_manager = theme_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize screenshot settings
        self.screenshot_settings = ScreenshotSettingsService()
        
        # Initialize automation services
        self.coordinates_manager = CoordinatesManager()
        self.automation_service = AutomationService(self.coordinates_manager)
        
        # Current chat state
        self.current_chat_id = None
        self.last_response_id = None  # Store the last response ID for conversation context
        
        # Auto screenshot state
        self.auto_screenshots_enabled = False
        self.auto_screenshots_interval = self.screenshot_settings.get_settings().get("auto_screenshots_interval", 5)  # seconds
        self.auto_screenshots_timer = None
        self.analysis_in_progress = False
        
        # Create widgets
        self.create_widgets()
        
        # Setup context menu after all widgets are created
        self.setup_context_menu()
        
        # Load initial chat
        self.load_initial_chat()
    
    def create_widgets(self):
        """Create chat widget components"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Chat display area
        self.create_chat_display()
        
        # Input area
        self.create_input_area()
    
    def create_chat_display(self):
        """Create modern chat display area"""
        # Chat messages frame
        chat_frame = ctk.CTkFrame(self)
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)
        
        # Messages text widget with modern styling
        self.messages_text = scrolledtext.ScrolledText(
            chat_frame,
            font=("Segoe UI", 12),
            wrap="word",
            height=20,
            bg="#f8f9fa",
            fg="#212529",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.messages_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure text tags for modern styling
        self.setup_text_tags()
    
    def setup_text_tags(self):
        """Setup text tags for modern message styling"""
        # User message styling (right-aligned, blue background)
        self.messages_text.tag_configure("user", 
            background="#007bff", 
            foreground="white",
            relief="raised",
            borderwidth=1,
            lmargin1=200,
            lmargin2=200,
            rmargin=50,
            spacing1=5,
            spacing2=5,
            spacing3=5,
            wrap="word"
        )
        
        # AI message styling (left-aligned, gray background)
        self.messages_text.tag_configure("assistant", 
            background="#e9ecef", 
            foreground="#212529",
            relief="raised",
            borderwidth=1,
            lmargin1=50,
            lmargin2=50,
            rmargin=200,
            spacing1=5,
            spacing2=5,
            spacing3=5,
            wrap="word"
        )
        
        # Error message styling (red background)
        self.messages_text.tag_configure("error", 
            background="#dc3545", 
            foreground="white",
            relief="raised",
            borderwidth=1,
            lmargin1=50,
            lmargin2=50,
            rmargin=50,
            spacing1=5,
            spacing2=5,
            spacing3=5,
            wrap="word"
        )
        
        # Timestamp styling
        self.messages_text.tag_configure("timestamp", 
            foreground="#6c757d",
            font=("Segoe UI", 10)
        )
        
        # Sender styling
        self.messages_text.tag_configure("sender", 
            foreground="#495057",
            font=("Segoe UI", 11, "bold")
        )
    
    def setup_context_menu(self):
        """Setup context menu for copy/paste functionality"""
        # Create context menu for messages text
        self.context_menu = tk.Menu(self.messages_text, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Выделить все", command=self.select_all)
        
        # Create context menu for message entry
        self.entry_context_menu = tk.Menu(self.message_entry, tearoff=0)
        self.entry_context_menu.add_command(label="Копировать", command=self.copy_text)
        self.entry_context_menu.add_command(label="Вставить", command=self.paste_text)
        self.entry_context_menu.add_separator()
        self.entry_context_menu.add_command(label="Выделить все", command=self.select_all)
        
        # Bind right-click to show context menu
        self.messages_text.bind("<Button-3>", self.show_context_menu)
        
        # Bind keyboard shortcuts for messages text
        self.messages_text.bind("<Control-c>", lambda e: self.copy_text())
        self.messages_text.bind("<Control-a>", lambda e: self.select_all())
        
        # Also bind to message entry
        self.message_entry.bind("<Button-3>", self.show_entry_context_menu)
        self.message_entry.bind("<Control-c>", lambda e: self.copy_text())
        self.message_entry.bind("<Control-v>", lambda e: self.paste_text())
        self.message_entry.bind("<Control-a>", lambda e: self.select_all())
        
        # Bind auto screenshot hotkey Ctrl+Shift+S to main window
        self.bind_hotkey()
    
    def show_context_menu(self, event):
        """Show context menu at cursor position"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def show_entry_context_menu(self, event):
        """Show context menu for message entry"""
        try:
            self.entry_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.entry_context_menu.grab_release()
    
    def copy_text(self):
        """Copy selected text to clipboard"""
        try:
            # Get selected text from messages text
            if self.messages_text.selection_get():
                selected_text = self.messages_text.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.logger.info("Text copied to clipboard")
        except tk.TclError:
            # No text selected
            pass
    
    def paste_text(self):
        """Paste text or image from clipboard"""
        try:
            self.logger.info("Paste operation triggered")
            
            # First try to paste as text
            try:
                clipboard_text = self.clipboard_get()
                if clipboard_text:
                    # Insert at cursor position in message entry
                    current_text = self.message_entry.get()
                    cursor_pos = self.message_entry.index(tk.INSERT)
                    new_text = current_text[:cursor_pos] + clipboard_text + current_text[cursor_pos:]
                    self.message_entry.delete(0, tk.END)
                    self.message_entry.insert(0, new_text)
                    self.logger.info("Text pasted from clipboard")
                    return
            except tk.TclError:
                # No text in clipboard, try image
                self.logger.debug("No text in clipboard, trying image")
            
            # Try to paste as image
            self.logger.info("Attempting to paste image from clipboard")
            if self.paste_image_from_clipboard():
                self.logger.info("Successfully pasted image from clipboard")
            else:
                self.logger.info("No image found in clipboard")
            
        except Exception as e:
            self.logger.error(f"Error pasting from clipboard: {e}")
    
    def paste_image_from_clipboard(self):
        """Paste image from clipboard and analyze it"""
        try:
            # First try simple PIL ImageGrab method
            try:
                from PIL import ImageGrab
                import tempfile
                
                # Try to grab image from clipboard
                image = ImageGrab.grabclipboard()
                
                if image is not None and hasattr(image, 'save'):
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        image.save(temp_file.name, 'PNG')
                        temp_path = temp_file.name
                    
                    # Analyze the image
                    self.analyze_uploaded_image(temp_path)
                    
                    # Clean up temp file after a delay
                    def cleanup_temp_file():
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    threading.Timer(10.0, cleanup_temp_file).start()
                    
                    self.logger.info("Image pasted and analyzed from clipboard (PIL ImageGrab)")
                    return True
                    
            except Exception as e:
                self.logger.debug(f"PIL ImageGrab method failed: {e}")
            
            # Fallback to win32clipboard method
            try:
                import win32clipboard
                from PIL import Image
                import tempfile
                
                # Try to get image from clipboard
                win32clipboard.OpenClipboard()
                try:
                    # Check if clipboard contains image data
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                        # Get image data
                        image_data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                        
                        # Close clipboard first
                        win32clipboard.CloseClipboard()
                        
                        # Convert DIB to PIL Image using simpler method
                        import win32ui
                        import win32con
                        
                        # Create a memory DC
                        hdc = win32ui.CreateDC()
                        hdc.CreateCompatibleDC()
                        hbmp = win32ui.CreateBitmap()
                        hbmp.CreateCompatibleBitmap(hdc, 1, 1)
                        
                        # Load the DIB data into bitmap
                        hdc.SelectObject(hbmp)
                        hdc.SetDIBitsToDevice(0, 0, 1, 1, 0, 0, 0, 1, image_data, None, win32con.DIB_RGB_COLORS)
                        
                        # Convert to PIL Image
                        bmpinfo = hbmp.GetInfo()
                        bmpstr = hbmp.GetBitmapBits(True)
                        image = Image.frombuffer(
                            'RGB',
                            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                            bmpstr, 'raw', 'BGRX', 0, 1
                        )
                        
                        # Clean up
                        hdc.DeleteDC()
                        hbmp.DeleteObject()
                        
                        # Save to temporary file
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                            image.save(temp_file.name, 'PNG')
                            temp_path = temp_file.name
                        
                        # Analyze the image
                        self.analyze_uploaded_image(temp_path)
                        
                        # Clean up temp file after a delay
                        def cleanup_temp_file():
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                        threading.Timer(10.0, cleanup_temp_file).start()
                        
                        self.logger.info("Image pasted and analyzed from clipboard (win32clipboard)")
                        return True
                        
                    else:
                        win32clipboard.CloseClipboard()
                        self.logger.debug("No image data in clipboard")
                        return False
                        
                except Exception as e:
                    try:
                        win32clipboard.CloseClipboard()
                    except:
                        pass
                    self.logger.debug(f"No image in clipboard: {e}")
                    return False
                    
            except ImportError as e:
                self.logger.debug(f"win32clipboard not available: {e}")
                return False
            except Exception as e:
                self.logger.debug(f"win32clipboard method failed: {e}")
                
        except Exception as e:
            self.logger.error(f"Error pasting image from clipboard: {e}")
            
        return False
    
    def select_all(self):
        """Select all text in the focused widget"""
        try:
            if self.focus_get() == self.messages_text:
                self.messages_text.tag_add(tk.SEL, "1.0", tk.END)
                self.messages_text.mark_set(tk.INSERT, "1.0")
                self.messages_text.see(tk.INSERT)
            elif self.focus_get() == self.message_entry:
                self.message_entry.select_range(0, tk.END)
        except Exception as e:
            self.logger.error(f"Error selecting text: {e}")
    
    def create_input_area(self):
        """Create modern input area"""
        # Input frame
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Message input
        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Введите ваше сообщение...",
            font=ctk.CTkFont(size=12),
            height=40
        )
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=10)
        
        # Send button
        send_btn = ctk.CTkButton(
            input_frame,
            text="📤",
            command=self.send_message,
            font=ctk.CTkFont(size=16),
            width=50,
            height=40
        )
        send_btn.grid(row=0, column=1, padx=(5, 10), pady=10)
        
        # Bind Enter key
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Quick screenshot button
        screenshot_btn = ctk.CTkButton(
            buttons_frame,
            text="📷 Быстрый скриншот",
            command=self.take_quick_screenshot,
            font=ctk.CTkFont(size=12),
            height=35,
            width=150
        )
        screenshot_btn.pack(side="left", padx=(10, 5), pady=10)
        
        # Attach image button
        attach_btn = ctk.CTkButton(
            buttons_frame,
            text="📎 Изображение",
            command=self.attach_image,
            font=ctk.CTkFont(size=12),
            height=35,
            width=120
        )
        attach_btn.pack(side="left", padx=5, pady=10)
        
        # Screenshot settings button
        settings_btn = ctk.CTkButton(
            buttons_frame,
            text="⚙️ Настройки",
            command=self.show_screenshot_dialog,
            font=ctk.CTkFont(size=12),
            height=35,
            width=120
        )
        settings_btn.pack(side="left", padx=5, pady=10)
        
        
        # New chat button
        new_chat_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Новый чат",
            command=self.create_new_chat,
            font=ctk.CTkFont(size=12),
            height=35,
            width=120
        )
        new_chat_btn.pack(side="right", padx=(5, 10), pady=10)
    
    def add_message(self, message, sender="assistant"):
        """Add message to chat with modern styling"""
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        
        # Add sender prefix and message
        if sender == "user":
            prefix = "👤 Вы"
            sender_tag = "user"
        elif sender == "assistant":
            prefix = "🤖 ИИ"
            sender_tag = "assistant"
        elif sender == "error":
            prefix = "❌ Ошибка"
            sender_tag = "error"
        else:
            prefix = "🤖 ИИ"
            sender_tag = "assistant"
        
        # Insert timestamp
        self.messages_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Insert sender prefix
        self.messages_text.insert(tk.END, f"{prefix}: ", "sender")
        
        # Insert message with appropriate styling
        self.messages_text.insert(tk.END, f"{message}\n\n", sender_tag)
        
        # Auto-scroll to bottom
        self.messages_text.see(tk.END)
        
        # Save message to chat manager
        if hasattr(self, 'current_chat_id') and self.current_chat_id:
            try:
                message_data = {
                    "content": message,
                    "sender": sender,
                    "timestamp": datetime.now().isoformat()
                }
                self.chat_manager.add_message(self.current_chat_id, message_data)
                self.logger.info(f"Message saved to chat {self.current_chat_id}")
            except Exception as e:
                self.logger.error(f"Error saving message: {e}")
    
    def send_message(self):
        """Send message to AI"""
        message = self.message_entry.get()
        if not message.strip():
            return
        
        # Add user message
        self.add_message(message, "user")
        
        # Clear input
        self.message_entry.delete(0, "end")
        
        # Send to API in background
        threading.Thread(target=self._send_to_api, args=(message,), daemon=True).start()
    
    def _send_to_api(self, message):
        """Send message to API (runs in background thread)"""
        try:
            # Send to API with previous response ID for conversation context
            response = self.api_client.send_message(message, self.last_response_id)
            
            if response and response.get("success") and response.get("message"):
                ai_response = response.get("message", "Нет ответа")
                # Store the response ID for next message
                self.last_response_id = response.get("response_id")
                self.after(0, lambda: self.add_message(ai_response, "assistant"))
                
                # Check for automation actions in the response
                self.after(0, lambda: self._check_and_execute_automation(ai_response))
            else:
                error_msg = response.get("error", "Неизвестная ошибка") if response else "Нет ответа от сервера"
                self.after(0, lambda: self.add_message(f"❌ {error_msg}", "error"))
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            self.after(0, lambda: self.add_message(f"❌ Ошибка отправки: {str(e)}", "error"))
    
    def _check_and_execute_automation(self, ai_response):
        """Check if AI response contains automation action and execute it"""
        try:
            self.logger.info(f"Checking automation for response: {ai_response[:100]}...")
            
            # Check if automation is enabled
            settings = self.screenshot_settings.get_settings()
            automation_enabled = settings.get("ai_automation_enabled", False)
            self.logger.info(f"Automation enabled: {automation_enabled}")
            
            if not automation_enabled:
                self.logger.info("Automation is disabled, skipping")
                return
            
            # Try to parse JSON from the response
            action = self._extract_action_from_response(ai_response)
            self.logger.info(f"Extracted action: {action}")
            
            if action:
                self.logger.info(f"AI automation triggered: {action}")
                
                # Show automation message
                self.add_message(f"🤖 Выполняю действие: {action}", "assistant")
                
                # Execute the action using new button system
                success = self.automation_service.perform_button_action(action)
                
                if success:
                    # Get button info for better user feedback
                    button_info = self.coordinates_manager.get_button_info(action)
                    button_name = button_info.get("name", action) if button_info else action
                    self.add_message(f"✅ Нажата кнопка '{button_name}' ({action})", "assistant")
                    self.logger.info(f"Automation button '{action}' executed successfully")
                else:
                    # Get available buttons for error message
                    available_buttons = self.coordinates_manager.get_available_button_ids()
                    self.add_message(f"❌ Кнопка '{action}' не найдена. Доступные кнопки: {', '.join(available_buttons)}", "error")
                    self.logger.error(f"Failed to execute automation action: {action}")
            else:
                self.logger.info("No valid action found in response")
                    
        except Exception as e:
            self.logger.error(f"Error in automation check: {e}")
    
    def _extract_action_from_response(self, response_text):
        """Extract button action from AI response text"""
        try:
            import json
            import re
            
            self.logger.info(f"Extracting action from response: {response_text[:200]}...")
            
            # Try to find JSON in the response text
            # Look for patterns like {"action": "button_name"}
            json_pattern = r'\{[^}]*"action"[^}]*\}'
            matches = re.findall(json_pattern, response_text)
            
            self.logger.info(f"Found {len(matches)} JSON matches: {matches}")
            
            if matches:
                for match in matches:
                    try:
                        data = json.loads(match)
                        action = data.get("action")
                        self.logger.info(f"Parsed action from JSON: {action}")
                        
                        if action:
                            # Check if this button exists in coordinates
                            available_buttons = self.coordinates_manager.get_available_button_ids()
                            
                            # First try direct match
                            if action in available_buttons:
                                self.logger.info(f"Direct button match found: {action}")
                                return action
                            
                            # Try legacy mapping for backward compatibility
                            action_map = {
                                "button_fold": "fold",
                                "button_call": "call", 
                                "button_raise": "raise",
                                "button_check": "check",
                                "fold": "fold",
                                "call": "call",
                                "raise": "raise",
                                "check": "check"
                            }
                            mapped_action = action_map.get(action)
                            
                            if mapped_action and mapped_action in available_buttons:
                                self.logger.info(f"Mapped action: {action} -> {mapped_action}")
                                return mapped_action
                            else:
                                self.logger.warning(f"Action '{action}' not found in available buttons: {available_buttons}")
                                
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"JSON decode error for match '{match}': {e}")
                        continue
            
            self.logger.info("No valid action found in response")
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting action from response: {e}")
            return None
    
    def take_quick_screenshot(self):
        """Take quick screenshot using saved settings"""
        try:
            settings = self.screenshot_settings.get_settings()
            screenshot_type = settings.get("screenshot_type", "fullscreen")
            prompt = settings.get("prompt", "")
            selected_app = settings.get("selected_app")
            
            self.logger.info(f"Taking quick screenshot with settings: type={screenshot_type}, app={selected_app}")
            if selected_app:
                self.logger.info(f"Selected app details: {selected_app}")
            
            # Use default prompt if not set
            if not prompt.strip():
                prompt = "Проанализируй этот скриншот максимально подробно на русском языке."
                self.logger.info("Using default prompt for screenshot analysis")
            
            # Hide main application window before taking screenshot
            self.logger.info("Hiding main application window for clean screenshot...")
            # Get the root window (main application window)
            root_window = self.winfo_toplevel()
            self.logger.info(f"Root window: {root_window}")
            if hasattr(root_window, 'withdraw'):
                root_window.withdraw()  # Hide the main window
                self.logger.info("Main window hidden successfully")
                
                # Add delay to ensure window is fully hidden before screenshot
                self.logger.info("Waiting for window to fully hide...")
                import time
                time.sleep(0.5)  # 500ms delay to ensure window is hidden
                self.logger.info("Delay completed, proceeding with screenshot")
            else:
                self.logger.warning("Cannot hide main window - withdraw method not available")
            
            screenshot_path = None
            
            # Take screenshot based on saved settings
            if screenshot_type == "fullscreen":
                self.logger.info("Attempting full screen screenshot...")
                screenshot_path = self.screenshot_service.capture_full_screen()
                self.logger.info(f"Full screen screenshot result: {screenshot_path}")
            elif (screenshot_type == "app" or screenshot_type == "application") and selected_app:
                # Check if selected_app is a string (from settings) or dict (from running app)
                if isinstance(selected_app, str):
                    # selected_app is a string from settings, need to find running app
                    self.logger.info(f"Selected app is string: {selected_app}")
                    # For now, fallback to fullscreen
                    self.add_message("⚠️ Настройки приложения требуют обновления. Делаю скриншот полного экрана.", "assistant")
                    screenshot_path = self.screenshot_service.capture_full_screen()
                elif isinstance(selected_app, dict):
                    # selected_app is a dict with app info
                    if self._is_app_still_running(selected_app):
                        # Hide all other windows for clean screenshot (same as in settings dialog)
                        self.logger.info(f"Hiding all windows except target app for clean screenshot...")
                        hidden_windows = self.screenshot_service._hide_all_windows_except(selected_app.get("hwnd"))
                        
                        try:
                            screenshot_path = self.screenshot_service.capture_application(
                                selected_app["pid"], 
                                selected_app.get("hwnd")
                            )
                        finally:
                            # Always restore hidden windows
                            if hidden_windows:
                                self.screenshot_service._restore_windows(hidden_windows)
                    else:
                        self.add_message(f"⚠️ Приложение '{selected_app.get('name', 'Unknown')}' не запущено. Делаю скриншот полного экрана.", "assistant")
                        screenshot_path = self.screenshot_service.capture_full_screen()
                else:
                    self.add_message("⚠️ Неизвестный формат настроек приложения. Делаю скриншот полного экрана.", "assistant")
                    screenshot_path = self.screenshot_service.capture_full_screen()
            else:
                self.add_message("⚠️ Настройки приложения неполные. Делаю скриншот полного экрана.", "assistant")
                screenshot_path = self.screenshot_service.capture_full_screen()
            
            if screenshot_path:
                self.add_message(f"📷 Скриншот сделан, анализирую...", "assistant")
                self.analyze_screenshot(screenshot_path, prompt)
            else:
                self.logger.warning("Screenshot failed, attempting retry...")
                # Try one more time with a small delay
                import time
                time.sleep(0.1)  # Small delay
                retry_screenshot_path = self.screenshot_service.capture_full_screen()
                self.logger.info(f"Retry screenshot result: {retry_screenshot_path}")
                
                if retry_screenshot_path:
                    self.add_message(f"📷 Скриншот сделан (повторная попытка), анализирую...", "assistant")
                    self.analyze_screenshot(retry_screenshot_path, prompt)
                else:
                    self.add_message("❌ Не удалось сделать скриншот. Проверьте настройки.", "error")
                
        except Exception as e:
            self.logger.error(f"Quick screenshot error: {e}")
            self.add_message(f"❌ Ошибка быстрого скриншота: {str(e)}", "error")
        finally:
            # Always restore main application window
            try:
                root_window = self.winfo_toplevel()
                if hasattr(root_window, 'deiconify'):
                    root_window.deiconify()  # Show the main window again
                    self.logger.info("Main application window restored")
                else:
                    self.logger.warning("Cannot restore main window - deiconify method not available")
            except Exception as e:
                self.logger.error(f"Error restoring main window: {e}")
    
    def analyze_screenshot(self, screenshot_path, prompt):
        """Analyze screenshot with AI"""
        # Show loading message
        self.add_message("🔄 Анализирую скриншот... Это может занять несколько секунд.", "assistant")
        
        # Start analysis in separate thread
        threading.Thread(target=self._analyze_screenshot_async, args=(screenshot_path, prompt), daemon=True).start()
    
    def _analyze_screenshot_async(self, screenshot_path, prompt):
        """Analyze screenshot asynchronously"""
        try:
            # Set analysis in progress flag
            self.analysis_in_progress = True
            
            # Update loading message
            self.after(0, lambda: self.add_message("🔄 Отправляю изображение на сервер...", "assistant"))
            
            # Send screenshot for analysis
            response = self.api_client.analyze_image(screenshot_path, prompt)
            
            if response and (response.get("success") or response.get("analysis")):
                # Try to get analysis from either 'analysis' or 'message' field
                analysis = response.get("analysis") or response.get("message", "No analysis received")
                
                # Add analysis to chat as AI message (for display)
                self.after(0, lambda: self.add_message(f"📷 Анализ скриншота:\n\n{analysis}", "assistant"))
                
                # Check for automation actions in the analysis
                self.after(0, lambda: self._check_and_execute_automation(analysis))
                
                # Now automatically send the analysis as a user message to OpenAI chat
                # This creates a proper conversation flow where the user can continue discussing the analysis
                self.logger.info("Sending screenshot analysis to OpenAI chat for context...")
                
                # Send analysis to OpenAI chat in a separate thread
                threading.Thread(target=self._send_analysis_to_chat, args=(analysis,), daemon=True).start()
                
                # Analysis is complete, user can now continue the conversation
                self.logger.info("Screenshot analysis completed")
                
            else:
                error_msg = response.get("error") or response.get("message", "Неизвестная ошибка") if response else "Нет ответа от сервера"
                self.after(0, lambda: self.add_message(f"❌ Ошибка анализа: {error_msg}", "error"))
                
        except Exception as e:
            self.logger.error(f"Image analysis error: {e}")
            self.after(0, lambda: self.add_message(f"❌ Ошибка анализа изображения: {str(e)}", "error"))
        finally:
            # Reset analysis in progress flag
            self.analysis_in_progress = False
    
    def _send_analysis_to_chat(self, analysis):
        """Send screenshot analysis to OpenAI chat for context with smart scheduling"""
        try:
            # Send the analysis as a user message to maintain conversation context
            self.logger.info("Sending analysis to OpenAI chat for context...")
            
            # Send analysis to OpenAI chat with conversation context
            response = self.api_client.send_message(analysis, self.last_response_id)
            
            if response and (response.get("response") or response.get("message")):
                # Try both possible response fields
                ai_response = response.get("response") or response.get("message", "No response received")
                # Store the response ID for next message
                self.last_response_id = response.get("response_id")
                self.after(0, lambda: self.add_message(ai_response, "assistant"))
                self.logger.info("Analysis successfully sent to OpenAI chat")
                
                # Smart scheduling: check if there's an action to execute
                self._handle_ai_response_with_smart_scheduling(ai_response)
                
            else:
                error_msg = response.get("error", "Неизвестная ошибка") if response else "Нет ответа от сервера"
                self.after(0, lambda: self.add_message(f"❌ Ошибка отправки анализа в чат: {error_msg}", "error"))
                # Take next screenshot even on error with delay
                self.after(100, self.take_auto_screenshot)  # 100ms delay
                
        except Exception as e:
            self.logger.error(f"Error sending analysis to chat: {e}")
            self.after(0, lambda: self.add_message(f"❌ Ошибка отправки анализа в чат: {str(e)}", "error"))
            # Take next screenshot even on error with delay
            self.after(100, self.take_auto_screenshot)  # 100ms delay
    
    def _handle_ai_response_with_smart_scheduling(self, ai_response):
        """Handle AI response with smart scheduling based on whether action is needed"""
        try:
            # Check if automation is enabled
            settings = self.screenshot_settings.get_settings()
            automation_enabled = settings.get("ai_automation_enabled", False)
            self.logger.info(f"Automation enabled: {automation_enabled}")
            
            if not automation_enabled:
                self.logger.info("Automation is disabled, scheduling next screenshot normally")
                self._schedule_next_screenshot_safe()
                return
            
            # Check if AI response contains an action
            action = self._extract_action_from_response(ai_response)
            
            if action:
                self.logger.info(f"AI response contains action: {action}, executing with smart scheduling")
                
                # Show action execution message
                self.after(0, lambda: self.add_message(f"🎯 Выполняю действие: {action}", "assistant"))
                
                # Execute the action
                success = self.automation_service.perform_button_action(action)
                
                if success:
                    # Get button info for better user feedback
                    button_info = self.coordinates_manager.get_button_info(action)
                    button_name = button_info.get("name", action) if button_info else action
                    self.after(0, lambda: self.add_message(f"✅ Нажата кнопка '{button_name}' ({action})", "assistant"))
                    self.logger.info(f"Action '{action}' executed successfully")
                    
                    # Take next screenshot after action with small delay
                    self.logger.info("Taking next screenshot after action with small delay")
                    self.after(100, self.take_auto_screenshot)  # 100ms delay
                    
                else:
                    # Get available buttons for error message
                    available_buttons = self.coordinates_manager.get_available_button_ids()
                    self.after(0, lambda: self.add_message(f"❌ Кнопка '{action}' не найдена. Доступные кнопки: {', '.join(available_buttons)}", "error"))
                    self.logger.error(f"Failed to execute action: {action}")
                    
                    # Fallback: take next screenshot anyway
                    self.logger.info("Taking next screenshot after failed action with small delay")
                    self.after(100, self.take_auto_screenshot)  # 100ms delay
                    
            else:
                self.logger.info("No action in AI response, taking next screenshot with small delay")
                # No action needed, take next screenshot with small delay
                self.after(100, self.take_auto_screenshot)  # 100ms delay
                
        except Exception as e:
            self.logger.error(f"Error in smart scheduling: {e}")
            # Fallback: take next screenshot anyway with delay
            self.after(100, self.take_auto_screenshot)  # 100ms delay
    
    def show_screenshot_dialog(self):
        """Show screenshot settings dialog"""
        try:
            from .screenshot_dialog import ScreenshotDialog
            dialog = ScreenshotDialog(self, self.screenshot_service, self.screenshot_settings, self.coordinates_manager)
            if dialog.result:
                self.logger.info("Screenshot settings updated")
                # Update auto screenshots interval if settings changed
                self.update_auto_screenshots_interval()
        except ImportError:
            self.add_message("⚠️ Диалог настроек скриншота недоступен", "error")
            self.logger.warning("ScreenshotDialog not available")
    
    def attach_image(self):
        """Attach image from file dialog"""
        try:
            from tkinter import filedialog
            
            # Open file dialog for image selection
            file_path = filedialog.askopenfilename(
                title="Выберите изображение",
                filetypes=[
                    ("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                    ("PNG файлы", "*.png"),
                    ("JPEG файлы", "*.jpg *.jpeg"),
                    ("Все файлы", "*.*")
                ]
            )
            
            if file_path:
                self.analyze_uploaded_image(file_path)
                
        except Exception as e:
            self.logger.error(f"Error attaching image: {e}")
            self.add_message(f"❌ Ошибка прикрепления изображения: {str(e)}", "error")
    
    def analyze_uploaded_image(self, image_path):
        """Analyze uploaded image"""
        try:
            # Validate file exists
            if not os.path.exists(image_path):
                self.add_message("❌ Файл изображения не найден", "error")
                return
            
            # Check file extension
            valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in valid_extensions:
                self.add_message("❌ Неподдерживаемый формат изображения", "error")
                return
            
            # Add message about image upload
            self.add_message(f"📎 Изображение загружено: {os.path.basename(image_path)}", "user")
            
            # Get prompt from screenshot settings
            prompt = self.screenshot_settings.settings.get("prompt", "Проанализируй это изображение")
            
            # Show progress
            self.add_message("🔄 Анализирую изображение...", "assistant")
            
            # Analyze image in background thread
            threading.Thread(
                target=self._analyze_uploaded_image_async, 
                args=(image_path, prompt), 
                daemon=True
            ).start()
            
        except Exception as e:
            self.logger.error(f"Error analyzing uploaded image: {e}")
            self.add_message(f"❌ Ошибка анализа изображения: {str(e)}", "error")
    
    def _analyze_uploaded_image_async(self, image_path, prompt):
        """Analyze uploaded image asynchronously"""
        try:
            # Analyze image using API
            response = self.api_client.analyze_image(image_path, prompt)
            
            if response and response.get("analysis"):
                analysis = response.get("analysis", "Анализ не получен")
                
                # Add analysis to chat as AI message (for display)
                self.after(0, lambda: self.add_message(f"📷 Анализ изображения:\n\n{analysis}", "assistant"))
                
                # Check for automation actions in the analysis
                self.after(0, lambda: self._check_and_execute_automation(analysis))
                
                # Now automatically send the analysis as a user message to OpenAI chat
                # This creates a proper conversation flow where the user can continue discussing the analysis
                self.logger.info("Sending image analysis to OpenAI chat for context...")
                
                # Send analysis to OpenAI chat in a separate thread
                threading.Thread(target=self._send_analysis_to_chat, args=(analysis,), daemon=True).start()
                
                # Analysis is complete, user can now continue the conversation
                self.logger.info("Image analysis completed")
                
            else:
                # Check if this is an error response from the API
                if response and response.get("error"):
                    error_msg = response.get("error", "Неизвестная ошибка")
                    self.after(0, lambda: self.add_message(f"❌ Ошибка анализа: {error_msg}", "error"))
                elif response and response.get("message"):
                    # Sometimes the API returns the analysis in "message" field instead of "analysis"
                    analysis = response.get("message", "Анализ не получен")
                    self.after(0, lambda: self.add_message(f"📷 Анализ изображения:\n\n{analysis}", "assistant"))
                    
                    # Check for automation actions in the analysis
                    self.after(0, lambda: self._check_and_execute_automation(analysis))
                    
                    # Send analysis to OpenAI chat
                    self.logger.info("Sending image analysis to OpenAI chat for context...")
                    threading.Thread(target=self._send_analysis_to_chat, args=(analysis,), daemon=True).start()
                    self.logger.info("Image analysis completed")
                else:
                    error_msg = "Нет ответа от сервера"
                    self.after(0, lambda: self.add_message(f"❌ Ошибка анализа: {error_msg}", "error"))
                
        except Exception as e:
            self.logger.error(f"Image analysis error: {e}")
            self.after(0, lambda: self.add_message(f"❌ Ошибка анализа изображения: {str(e)}", "error"))
    
    def create_new_chat(self):
        """Create a new chat"""
        try:
            import uuid
            chat_id = str(uuid.uuid4())
            self.chat_manager.create_chat(chat_id, "Новый чат")
            self.current_chat_id = chat_id
            self.messages_text.delete("1.0", tk.END)
            
            # Add welcome message without saving to chat manager (it's a system message)
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M")
            self.messages_text.insert(tk.END, f"[{timestamp}] 🤖 ИИ: 👋 Новый чат создан! Чем могу помочь?\n\n")
            self.messages_text.see(tk.END)
            
            self.logger.info(f"Created new chat: {chat_id}")
            
            # Notify parent to update sidebar - try multiple ways to find the main window
            parent = self.master
            while parent and not hasattr(parent, 'load_chats_to_sidebar'):
                parent = parent.master
            
            if parent and hasattr(parent, 'load_chats_to_sidebar'):
                parent.load_chats_to_sidebar()
                # Also update button states for the new chat
                if hasattr(parent, 'update_chat_buttons_state'):
                    parent.update_chat_buttons_state(chat_id)
                self.logger.info("Notified parent to update sidebar")
            else:
                self.logger.warning("Could not find parent with load_chats_to_sidebar method")
                
        except Exception as e:
            self.logger.error(f"Error creating new chat: {e}")
            self.add_message(f"❌ Ошибка создания чата: {str(e)}", "error")
    
    def load_initial_chat(self):
        """Load initial chat"""
        try:
            chats = self.chat_manager.get_all_chats()
            if chats:
                # Get first chat ID
                first_chat_id = list(chats.keys())[0]
                self.current_chat_id = first_chat_id
                self.load_messages()
            else:
                self.create_new_chat()
        except Exception as e:
            self.logger.error(f"Error loading initial chat: {e}")
            self.create_new_chat()
    
    def load_messages(self):
        """Load messages for current chat"""
        if not self.current_chat_id:
            return
        
        try:
            messages = self.chat_manager.get_messages(self.current_chat_id)
            self.messages_text.delete("1.0", tk.END)
            
            for message in messages:
                sender = message.get("sender", "assistant")
                content = message.get("content", "")
                self.add_message(content, sender)
            
            self.logger.info(f"Loaded {len(messages)} messages for chat {self.current_chat_id}")
            
        except Exception as e:
            self.logger.error(f"Error loading messages: {e}")
    
    def set_current_chat(self, chat_id):
        """Set current chat and load its messages"""
        try:
            self.current_chat_id = chat_id
            # Reset response ID when switching chats to start fresh conversation
            self.last_response_id = None
            self.load_messages()
            self.logger.info(f"Switched to chat: {chat_id}")
        except Exception as e:
            self.logger.error(f"Error switching to chat {chat_id}: {e}")
            self.add_message(f"❌ Ошибка переключения чата: {str(e)}", "error")
    
    def _is_app_still_running(self, app_info):
        """Check if application is still running"""
        try:
            import psutil
            return psutil.pid_exists(app_info.get("pid", 0))
        except Exception:
            return False
    
    # Auto Screenshot Methods
    def toggle_auto_screenshots(self):
        """Toggle auto screenshot mode"""
        self.auto_screenshots_enabled = not self.auto_screenshots_enabled
        
        if self.auto_screenshots_enabled:
            self.start_auto_screenshots()
        else:
            self.stop_auto_screenshots()
        
        self.update_window_title()
        self.add_message(f"🔄 Автоматические скриншоты: {'ВКЛ' if self.auto_screenshots_enabled else 'ВЫКЛ'}", "assistant")
    
    def start_auto_screenshots(self):
        """Start automatic screenshots in chain mode"""
        if not self.auto_screenshots_enabled:
            return
        
        self.logger.info("Starting auto screenshots in chain mode")
        # Start immediately with first screenshot
        self.take_auto_screenshot()
    
    def stop_auto_screenshots(self):
        """Stop automatic screenshots"""
        if self.auto_screenshots_timer:
            self.after_cancel(self.auto_screenshots_timer)
            self.auto_screenshots_timer = None
    
    def schedule_next_screenshot(self):
        """Schedule next screenshot based on interval and analysis status"""
        if not self.auto_screenshots_enabled:
            return
        
        # Cancel existing timer
        if self.auto_screenshots_timer:
            self.after_cancel(self.auto_screenshots_timer)
        
        # Schedule next screenshot
        self.auto_screenshots_timer = self.after(self.auto_screenshots_interval * 1000, self.take_auto_screenshot)
    
    def take_auto_screenshot(self):
        """Take automatic screenshot in chain mode"""
        if not self.auto_screenshots_enabled:
            return
        
        # Check if analysis is in progress - if yes, wait a bit and retry
        if self.analysis_in_progress:
            self.logger.info("Analysis in progress, waiting 200ms and retrying...")
            self.after(200, self.take_auto_screenshot)
            return
        
        # Take screenshot using existing method
        try:
            self.logger.info("Taking auto screenshot in chain mode")
            # Call take_quick_screenshot in a way that won't cause recursion issues
            self.take_quick_screenshot()
            # Note: Next screenshot will be triggered by _send_analysis_to_chat after analysis
        except Exception as e:
            self.logger.error(f"Auto screenshot error: {e}")
            # On error, wait a bit and retry
            self.after(1000, self.take_auto_screenshot)
    
    def update_window_title(self):
        """Update window title to show auto screenshot status"""
        try:
            # Find the main window
            root = self.winfo_toplevel()
            if hasattr(root, 'title'):
                base_title = "🤖 AI Чат Помощник - Modern"
                if self.auto_screenshots_enabled:
                    title = f"{base_title} - Автоскриншоты: ВКЛ (цепочка)"
                else:
                    title = base_title
                root.title(title)
        except Exception as e:
            self.logger.error(f"Error updating window title: {e}")
    
    def update_auto_screenshots_interval(self):
        """Update auto screenshots interval from settings"""
        try:
            new_interval = self.screenshot_settings.get_settings().get("auto_screenshots_interval", 5)
            if new_interval != self.auto_screenshots_interval:
                self.auto_screenshots_interval = new_interval
                # Restart auto screenshots if they're enabled to use new interval
                if self.auto_screenshots_enabled:
                    self.stop_auto_screenshots()
                    self.start_auto_screenshots()
                self.update_window_title()
        except Exception as e:
            self.logger.error(f"Error updating auto screenshots interval: {e}")
    
    def bind_hotkey(self):
        """Bind global hotkey for auto screenshots"""
        try:
            # Get the main window (root)
            root = self.winfo_toplevel()
            
            # Bind to main window
            root.bind_all("<Control-Shift-S>", lambda e: self.toggle_auto_screenshots())
            
            # Also bind to self as backup
            self.bind("<Control-Shift-S>", lambda e: self.toggle_auto_screenshots())
            
            # Bind to message entry as backup
            self.message_entry.bind("<Control-Shift-S>", lambda e: self.toggle_auto_screenshots())
            
            self.logger.info("Auto screenshot hotkey Ctrl+Shift+S bound successfully")
        except Exception as e:
            self.logger.error(f"Error binding hotkey: {e}")
    
