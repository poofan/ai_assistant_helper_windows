"""
Chat Widget - Main chat interface with message display and input
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import logging
from datetime import datetime
from pathlib import Path
from .themes import ThemeManager
from services.screenshot_settings import ScreenshotSettingsService
from utils.markdown_renderer import MarkdownRenderer

class ChatWidget(tk.Frame):
    """Main chat interface widget"""
    
    def __init__(self, parent, api_client, screenshot_service, chat_manager, main_window=None):
        super().__init__(parent)
        self.api_client = api_client
        self.screenshot_service = screenshot_service
        self.chat_manager = chat_manager
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Theme manager
        self.theme_manager = ThemeManager()
        
        # Screenshot settings service
        self.screenshot_settings = ScreenshotSettingsService()
        
        # Chat state
        self.messages = []
        self.current_chat_id = None
        
        self.create_widgets()
        
        # Initialize Markdown renderer after widgets are created
        self.markdown_renderer = None
    
    def create_widgets(self):
        """Create chat interface widgets"""
        # Main chat area
        self.create_chat_display()
        
        # Input area
        self.create_input_area()
    
    def create_chat_display(self):
        """Create chat message display area"""
        theme = self.theme_manager.get_theme()
        
        # Chat messages frame
        chat_frame = tk.Frame(self, bg=theme.colors['bg_primary'])
        chat_frame.grid(row=0, column=0, sticky="nsew")
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        # Messages text widget with scrollbar
        self.messages_text = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=theme.fonts['message'],
            bg=theme.colors['chat_bg'],
            fg=theme.colors['text_primary'],
            relief='flat',
            borderwidth=0,
            highlightthickness=0,
            padx=0,
            pady=0
        )
        self.messages_text.grid(row=0, column=0, sticky="nsew")
        
        # Initialize Markdown renderer
        try:
            self.markdown_renderer = MarkdownRenderer(self.messages_text)
            self.markdown_renderer.set_theme_manager(self.theme_manager)
            self.logger.info("Markdown renderer initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Markdown renderer: {e}")
            self.markdown_renderer = None
        
        # Configure text tags for modern chat styling
        self.messages_text.tag_configure("user", 
                                       foreground=theme.colors['message_user_text'],
                                       background=theme.colors['message_user_bg'],
                                       font=theme.fonts['message'],
                                       relief='flat',
                                       borderwidth=0,
                                       lmargin1=50,
                                       lmargin2=20,
                                       rmargin=20,
                                       spacing1=8,
                                       spacing2=4,
                                       spacing3=8)
        self.messages_text.tag_configure("assistant", 
                                       foreground=theme.colors['message_ai_text'],
                                       background=theme.colors['message_ai_bg'],
                                       font=theme.fonts['message'],
                                       relief='flat',
                                       borderwidth=0,
                                       lmargin1=20,
                                       lmargin2=50,
                                       rmargin=20,
                                       spacing1=8,
                                       spacing2=4,
                                       spacing3=8)
        self.messages_text.tag_configure("timestamp", 
                                       foreground=theme.colors['text_muted'], 
                                       font=theme.fonts['timestamp'])
        self.messages_text.tag_configure("error", 
                                       foreground=theme.colors['message_error_text'],
                                       background=theme.colors['message_error_bg'],
                                       font=theme.fonts['message'],
                                       relief='flat',
                                       borderwidth=0,
                                       lmargin1=20,
                                       lmargin2=20,
                                       rmargin=20,
                                       spacing1=8,
                                       spacing2=4,
                                       spacing3=8)
    
    def create_input_area(self):
        """Create message input area"""
        theme = self.theme_manager.get_theme()
        
        input_frame = tk.Frame(self, bg=theme.colors['bg_primary'])
        input_frame.grid(row=1, column=0, sticky="ew", padx=(0, 0), pady=(5, 0))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Message input
        self.message_var = tk.StringVar()
        self.message_entry = tk.Text(
            input_frame, 
            height=3, 
            wrap=tk.WORD,
            font=theme.fonts['message'],
            bg=theme.colors['input_bg'],
            fg=theme.colors['input_text'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=theme.colors['input_focus'],
            highlightbackground=theme.colors['input_border']
        )
        self.message_entry.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Buttons frame
        buttons_frame = tk.Frame(input_frame, bg=theme.colors['bg_primary'])
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Send button
        ttk.Button(buttons_frame, text="Send", command=self.send_message).pack(side="right")
        
        # Quick screenshot button (with saved settings)
        ttk.Button(buttons_frame, text="📷 Быстрый скриншот", command=self.take_quick_screenshot).pack(side="right")
        
        # Screenshot settings button
        ttk.Button(buttons_frame, text="⚙️ Настройки скриншота", command=self.show_screenshot_dialog).pack(side="right")
        
        # Bind Enter key (Ctrl+Enter for new line)
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
        self.message_entry.bind('<Return>', lambda e: self.send_message() if not e.state & 0x4 else None)
    
    def apply_theme(self, theme):
        """Apply theme to chat widget"""
        # Apply to main frame
        self.configure(bg=theme.colors['bg_primary'])
        
        # Apply to messages text widget
        self.messages_text.configure(
            bg=theme.colors['chat_bg'],
            fg=theme.colors['text_primary'],
            font=theme.fonts['message'],
            insertbackground=theme.colors['text_primary']
        )
        
        # Update Markdown renderer theme if available
        if self.markdown_renderer:
            self.markdown_renderer.set_theme_manager(self.theme_manager)
        
        # Apply to message entry
        self.message_entry.configure(
            bg=theme.colors['input_bg'],
            fg=theme.colors['input_text'],
            font=theme.fonts['message'],
            highlightcolor=theme.colors['input_focus'],
            highlightbackground=theme.colors['input_border'],
            insertbackground=theme.colors['input_text']
        )
        
        # Apply theme to all child widgets
        self.apply_widget_theme(self, theme)
        
        # Update text tags for modern chat styling
        self.messages_text.tag_configure("user", 
                                       foreground=theme.colors['message_user_text'],
                                       background=theme.colors['message_user_bg'],
                                       font=theme.fonts['message'],
                                       relief='flat',
                                       borderwidth=0,
                                       lmargin1=50,
                                       lmargin2=20,
                                       rmargin=20,
                                       spacing1=8,
                                       spacing2=4,
                                       spacing3=8)
        self.messages_text.tag_configure("assistant", 
                                       foreground=theme.colors['message_ai_text'],
                                       background=theme.colors['message_ai_bg'],
                                       font=theme.fonts['message'],
                                       relief='flat',
                                       borderwidth=0,
                                       lmargin1=20,
                                       lmargin2=50,
                                       rmargin=20,
                                       spacing1=8,
                                       spacing2=4,
                                       spacing3=8)
        self.messages_text.tag_configure("timestamp", 
                                       foreground=theme.colors['text_muted'], 
                                       font=theme.fonts['timestamp'])
        self.messages_text.tag_configure("error", 
                                       foreground=theme.colors['message_error_text'],
                                       background=theme.colors['message_error_bg'],
                                       font=theme.fonts['message'],
                                       relief='flat',
                                       borderwidth=0,
                                       lmargin1=20,
                                       lmargin2=20,
                                       rmargin=20,
                                       spacing1=8,
                                       spacing2=4,
                                       spacing3=8)
        
        self.logger.info(f"Applied theme to chat widget")
    
    def apply_widget_theme(self, parent, theme):
        """Recursively apply theme to all child widgets"""
        for child in parent.winfo_children():
            widget_type = child.winfo_class()
            
            if widget_type == 'Frame':
                child.configure(bg=theme.colors['bg_primary'])
            elif widget_type == 'TFrame':
                # ttk.Frame doesn't support bg, skip
                pass
            elif widget_type == 'Text':
                child.configure(
                    bg=theme.colors['input_bg'],
                    fg=theme.colors['input_text'],
                    insertbackground=theme.colors['input_text']
                )
            
            # Recursively apply to children
            if hasattr(child, 'winfo_children'):
                self.apply_widget_theme(child, theme)
    
    def add_message(self, message, sender="user"):
        """Add a message to the chat display and save to ChatManager"""
        # Display message
        self._display_message(message, sender)
        
        # Create message data
        timestamp = datetime.now().strftime("%H:%M:%S")
        message_data = {
            "content": message,
            "sender": sender,
            "timestamp": timestamp,
            "response_id": None  # Will be set for AI responses
        }
        
        # Store in local messages
        self.messages.append(message_data)
        
        # Save to ChatManager if we have a current chat
        if self.current_chat_id:
            self.chat_manager.add_message(self.current_chat_id, message_data)
    
    def _display_message(self, message, sender="user"):
        """Display a message in the chat widget"""
        self.messages_text.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add sender
        if sender == "user":
            self.messages_text.insert(tk.END, "Вы: ", "user")
        elif sender == "assistant":
            self.messages_text.insert(tk.END, "ИИ: ", "assistant")
        elif sender == "error":
            self.messages_text.insert(tk.END, "Ошибка: ", "error")
        
        # Add message with modern chat styling
        if sender == "assistant":
            if self.markdown_renderer:
                # Use Markdown renderer for AI messages
                self.logger.info(f"Rendering Markdown for assistant message: {message[:100]}...")
                try:
                    # Apply assistant tag to the message content
                    start_pos = self.messages_text.index(tk.END + "-1c")
                    self.markdown_renderer.render_markdown(message)
                    end_pos = self.messages_text.index(tk.END + "-1c")
                    # Apply assistant styling to the entire message
                    self.messages_text.tag_add("assistant", start_pos, end_pos)
                    self.messages_text.insert(tk.END, "\n")  # Add extra line after markdown
                except Exception as e:
                    self.logger.error(f"Markdown rendering error: {e}")
                    # Fallback to regular text with styling
                    self.messages_text.insert(tk.END, f"{message}\n\n", "assistant")
            else:
                self.logger.warning("Markdown renderer not available, using regular text")
                self.messages_text.insert(tk.END, f"{message}\n\n", "assistant")
        elif sender == "user":
            # User messages with blue background (right-aligned style)
            self.messages_text.insert(tk.END, f"{message}\n\n", "user")
        else:  # error
            # Error messages with light red background
            self.messages_text.insert(tk.END, f"{message}\n\n", "error")
        
        # Auto-scroll to bottom
        self.messages_text.see(tk.END)
        self.messages_text.config(state=tk.DISABLED)
    
    def send_message(self):
        """Send a message to the AI"""
        # Check authentication
        if self.main_window and not self.main_window.is_authenticated:
            messagebox.showwarning("Ошибка", "Необходимо войти в систему для отправки сообщений")
            self.main_window.show_login_dialog()
            return
            
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.message_entry.delete("1.0", tk.END)
        
        # Add user message to chat
        self.add_message(message, "user")
        
        # Send to API in a separate thread
        threading.Thread(target=self._send_to_api, args=(message,), daemon=True).start()
    
    def _send_to_api(self, message):
        """Send message to API (runs in separate thread)"""
        try:
            # Show progress indicator
            self.master.after(0, lambda: self.add_message("🔄 Отправляю сообщение...", "assistant"))
            
            # Get previous response ID for context
            previous_response_id = None
            if self.messages:
                # Find the last AI message with response_id
                for msg in reversed(self.messages):
                    if msg["sender"] == "assistant" and msg.get("response_id"):
                        previous_response_id = msg["response_id"]
                        break
            
            # Log context for debugging
            self.logger.info(f"Sending message with context: previous_response_id={previous_response_id}")
            
            # Update progress
            self.master.after(0, lambda: self.add_message("🔄 Получаю ответ от AI...", "assistant"))
            
            # Send to API
            response = self.api_client.send_message(message, previous_response_id)
            
            if response and response.get("success"):
                # Add AI response to chat
                ai_message = response.get("message", "Ответ не получен")
                response_id = response.get("response_id")
                
                # Add message to display
                self.add_message(ai_message, "assistant")
                
                # Update the last message with response_id
                if self.messages and self.messages[-1]["sender"] == "assistant":
                    self.messages[-1]["response_id"] = response_id
                    
                    # Update in ChatManager
                    if self.current_chat_id:
                        # Find the last assistant message in ChatManager and update it
                        chat_messages = self.chat_manager.get_messages(self.current_chat_id)
                        for i in range(len(chat_messages) - 1, -1, -1):
                            if chat_messages[i]["sender"] == "assistant":
                                chat_messages[i]["response_id"] = response_id
                                break
            else:
                # Handle different error types
                error_type = response.get("error", "unknown_error") if response else "no_response"
                error_msg = response.get("message", "Неизвестная ошибка") if response else "Нет ответа от сервера"
                
                if error_type == "unauthorized":
                    # Token expired - need to re-login
                    self.add_message("🔐 Сессия истекла. Необходимо войти заново.", "error")
                    # Trigger re-login in main window
                    self.master.master.show_login_dialog()
                elif error_type == "payment_required":
                    # Payment required - show subscription info
                    self.add_message("💳 Недостаточно средств для выполнения запроса.", "error")
                    self.show_subscription_error(response)
                else:
                    # Other errors
                    self.add_message(f"❌ Ошибка: {error_msg}", "error")
                
        except Exception as e:
            self.logger.error(f"API error: {e}")
            self.add_message(f"Ошибка: {str(e)}", "error")
    
    def take_quick_screenshot(self):
        """Take a screenshot using saved settings"""
        # Check authentication
        if self.main_window and not self.main_window.is_authenticated:
            messagebox.showwarning("Ошибка", "Необходимо войти в систему для создания скриншотов")
            self.main_window.show_login_dialog()
            return
            
        try:
            # Get saved settings
            settings = self.screenshot_settings.get_settings()
            screenshot_type = settings.get("screenshot_type", "fullscreen")
            prompt = settings.get("prompt", "")
            selected_app = settings.get("selected_app")
            
            self.logger.info(f"Taking quick screenshot with settings: type={screenshot_type}, app={selected_app}")
            
            # Use default prompt if not set
            if not prompt.strip():
                prompt = "Проанализируй этот скриншот максимально подробно на русском языке. Опиши все элементы интерфейса, текст, изображения, цвета, расположение элементов, функциональные кнопки, меню, статусы, ошибки, предупреждения, и любые другие детали. Если это веб-страница - укажи URL, заголовок, содержимое. Если это приложение - опиши его функциональность и текущее состояние. Будь максимально детальным и точным в описании."
                self.logger.info("Using default prompt for screenshot analysis")
            
            # Take screenshot based on saved settings
            if screenshot_type == "fullscreen":
                screenshot_path = self.screenshot_service.capture_full_screen()
            elif screenshot_type == "application" and selected_app:
                # Check if selected app is still running
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
                    # Fallback to fullscreen if app is not running
                    self.logger.warning(f"Selected app '{selected_app.get('name', 'Unknown')}' is not running, falling back to fullscreen")
                    self.add_message(f"⚠️ Приложение '{selected_app.get('name', 'Unknown')}' не запущено. Делаю скриншот полного экрана.", "assistant")
                    screenshot_path = self.screenshot_service.capture_full_screen()
            else:
                # Fallback to fullscreen if settings are incomplete
                self.logger.warning("Incomplete screenshot settings, falling back to fullscreen")
                self.add_message("⚠️ Настройки приложения неполные. Делаю скриншот полного экрана.", "assistant")
                screenshot_path = self.screenshot_service.capture_full_screen()
            
            if screenshot_path:
                # Determine app name based on what was actually captured
                if screenshot_type == "fullscreen" or not selected_app:
                    app_name = "Полный экран"
                elif screenshot_type == "application" and selected_app and self._is_app_still_running(selected_app):
                    app_name = selected_app.get('name', 'Приложение')
                else:
                    app_name = "Полный экран (fallback)"
                
                self.add_message(f"📷 Скриншот {app_name} сделан, анализирую...", "assistant")
                
                # Analyze screenshot with prompt
                self.analyze_screenshot(screenshot_path, prompt)
            else:
                self.add_message("❌ Не удалось сделать скриншот. Проверьте настройки.", "error")
                
        except Exception as e:
            self.logger.error(f"Quick screenshot error: {e}")
            self.add_message(f"❌ Ошибка быстрого скриншота: {str(e)}", "error")
    
    def _is_app_still_running(self, selected_app):
        """Check if the selected application is still running"""
        try:
            import psutil
            pid = selected_app.get("pid")
            if not pid:
                return False
            
            # Check if process is still running
            try:
                process = psutil.Process(pid)
                # Check if process is still alive
                return process.is_running()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return False
        except Exception as e:
            self.logger.error(f"Error checking if app is running: {e}")
            return False
    
    def take_screenshot(self):
        """Take a screenshot and analyze it"""
        try:
            # Show screenshot options dialog
            self.show_screenshot_dialog()
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            self.add_message(f"Screenshot error: {str(e)}", "error")
    
    def show_screenshot_dialog(self):
        """Show screenshot options dialog"""
        # Check authentication
        if self.main_window and not self.main_window.is_authenticated:
            messagebox.showwarning("Ошибка", "Необходимо войти в систему для создания скриншотов")
            self.main_window.show_login_dialog()
            return
            
        dialog = ScreenshotDialog(self, self.screenshot_service, self.api_client, self)
        self.wait_window(dialog.dialog)
    
    def analyze_screenshot(self, screenshot_path, prompt):
        """Analyze screenshot with AI and integrate into chat context"""
        # Show loading indicator immediately
        self.add_message("🔄 Анализирую скриншот... Это может занять несколько секунд.", "assistant")
        
        # Start analysis in separate thread to avoid blocking UI
        threading.Thread(target=self._analyze_screenshot_async, args=(screenshot_path, prompt), daemon=True).start()
    
    def _analyze_screenshot_async(self, screenshot_path, prompt):
        """Analyze screenshot asynchronously"""
        try:
            # Update loading message
            self.master.after(0, lambda: self._update_loading_message("🔄 Отправляю изображение на сервер..."))
            
            # Send screenshot for analysis
            response = self.api_client.analyze_image(screenshot_path, prompt)
            
            if response and response.get("success"):
                analysis = response.get("message", "No analysis received")
                
                # Update loading message
                self.master.after(0, lambda: self._update_loading_message("🔄 Получен анализ, отправляю в чат..."))
                
                # Add analysis to chat as AI message (for display)
                self.master.after(0, lambda: self.add_message(f"Screenshot analysis: {analysis}", "assistant"))
                
                # Now automatically send the analysis as a user message to OpenAI chat
                # This creates a proper conversation flow where the user can continue discussing the analysis
                self.logger.info("Sending screenshot analysis to OpenAI chat for context...")
                
                # Send analysis to OpenAI chat in a separate thread
                threading.Thread(target=self._send_analysis_to_chat, args=(analysis,), daemon=True).start()
                
            else:
                # Handle different error types
                error_type = response.get("error", "unknown_error") if response else "no_response"
                error_msg = response.get("message", "Неизвестная ошибка") if response else "Нет ответа от сервера"
                
                if error_type == "unauthorized":
                    # Token expired - need to re-login
                    self.master.after(0, lambda: self.add_message("🔐 Сессия истекла. Необходимо войти заново.", "error"))
                    # Trigger re-login in main window
                    self.master.after(0, lambda: self.master.master.show_login_dialog())
                elif error_type == "payment_required":
                    # Payment required - show subscription info
                    self.master.after(0, lambda: self.add_message("💳 Недостаточно средств для анализа изображения.", "error"))
                    self.master.after(0, lambda: self.show_subscription_error(response))
                else:
                    # Other errors
                    self.master.after(0, lambda: self.add_message(f"❌ Ошибка анализа: {error_msg}", "error"))
                
        except Exception as e:
            self.logger.error(f"Image analysis error: {e}")
            self.master.after(0, lambda: self.add_message(f"❌ Ошибка анализа изображения: {str(e)}", "error"))
    
    def _update_loading_message(self, message):
        """Update the last loading message in chat"""
        try:
            # Simply add a new loading message instead of trying to update
            self.add_message(message, "assistant")
        except Exception as e:
            self.logger.error(f"Error updating loading message: {e}")
    
    def _send_analysis_to_chat(self, analysis):
        """Send screenshot analysis to OpenAI chat for context (runs in separate thread)"""
        try:
            # Show progress indicator
            self.master.after(0, lambda: self.add_message("🔄 Отправляю анализ в чат...", "assistant"))
            
            # Get previous response ID for context
            previous_response_id = None
            if self.messages:
                # Find the last AI message with response_id
                for msg in reversed(self.messages):
                    if msg["sender"] == "assistant" and msg.get("response_id"):
                        previous_response_id = msg["response_id"]
                        break
            
            # Send analysis as a user message to OpenAI chat
            message = f"Я проанализировал скриншот. Вот анализ: {analysis}"
            
            self.logger.info(f"Sending analysis to OpenAI chat with context: previous_response_id={previous_response_id}")
            
            # Update progress
            self.master.after(0, lambda: self.add_message("🔄 Получаю ответ от AI...", "assistant"))
            
            # Send to API
            response = self.api_client.send_message(message, previous_response_id)
            
            if response and response.get("success"):
                # Add AI response to chat
                ai_message = response.get("message", "Ответ не получен")
                response_id = response.get("response_id")
                
                # Add message to display
                self.add_message(ai_message, "assistant")
                
                # Update the last message with response_id
                if self.messages and self.messages[-1]["sender"] == "assistant":
                    self.messages[-1]["response_id"] = response_id
                    
                    # Update in ChatManager
                    if self.current_chat_id:
                        # Find the last assistant message in ChatManager and update it
                        chat_messages = self.chat_manager.get_messages(self.current_chat_id)
                        for i in range(len(chat_messages) - 1, -1, -1):
                            if chat_messages[i]["sender"] == "assistant":
                                chat_messages[i]["response_id"] = response_id
                                break
                
                self.logger.info("Screenshot analysis successfully integrated into chat context")
            else:
                error_msg = response.get("error", "Произошла неизвестная ошибка") if response else "Нет ответа от сервера"
                self.add_message(f"Не удалось интегрировать анализ: {error_msg}", "error")
                
        except Exception as e:
            self.logger.error(f"Analysis integration error: {e}")
            self.add_message(f"Ошибка интеграции анализа: {str(e)}", "error")
    
    def set_current_chat(self, chat_id):
        """Set the current chat ID"""
        self.current_chat_id = chat_id
        self.logger.info(f"Set current chat: {chat_id}")
    
    def load_messages(self, messages):
        """Load messages from ChatManager"""
        self.clear_chat()
        self.messages = messages.copy()
        
        # Ensure Markdown renderer is available
        if not self.markdown_renderer:
            try:
                self.markdown_renderer = MarkdownRenderer(self.messages_text)
                self.markdown_renderer.set_theme_manager(self.theme_manager)
                self.logger.info("Markdown renderer initialized in load_messages")
            except Exception as e:
                self.logger.error(f"Failed to initialize Markdown renderer in load_messages: {e}")
        
        # Display messages
        for msg in messages:
            self._display_message(msg["content"], msg["sender"])
        
        self.logger.info(f"Loaded {len(messages)} messages")
    
    def clear_chat(self):
        """Clear the chat display"""
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete("1.0", tk.END)
        self.messages_text.config(state=tk.DISABLED)
        self.messages.clear()
    
    def show_subscription_error(self, response):
        """Show subscription error dialog"""
        from .subscription_dialog import SubscriptionDialog
        
        # Create subscription dialog
        subscription_dialog = SubscriptionDialog(
            self, 
            response.get("subscription_status", {}),
            response.get("available_plans", []),
            response.get("credit_packages", []),
            response.get("purchase_url", "")
        )
        
        # Wait for dialog result
        self.wait_window(subscription_dialog.dialog)

class ScreenshotDialog:
    """Screenshot options dialog"""
    
    def __init__(self, parent, screenshot_service, api_client, chat_widget):
        self.screenshot_service = screenshot_service
        self.api_client = api_client
        self.chat_widget = chat_widget
        self.logger = logging.getLogger(__name__)
        self.theme_manager = ThemeManager()
        self.screenshot_settings = ScreenshotSettingsService()
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Опции скриншота")
        self.dialog.geometry("600x600")
        self.dialog.resizable(True, True)
        self.dialog.minsize(600, 500)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set dialog icon
        try:
            icon_path = Path("images") / "logo.png"
            if icon_path.exists():
                icon_image = tk.PhotoImage(file=str(icon_path))
                self.dialog.iconphoto(True, icon_image)
        except Exception as e:
            self.logger.error(f"Failed to load dialog icon: {e}")
        
        # Apply theme to dialog
        theme = self.theme_manager.get_theme()
        self.dialog.configure(bg=theme.colors['bg_primary'])
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
    
    def _get_current_quick_settings_text(self, settings):
        """Get text description of current quick screenshot settings"""
        screenshot_type = settings.get("screenshot_type", "fullscreen")
        selected_app = settings.get("selected_app")
        prompt = settings.get("prompt", "")
        
        if screenshot_type == "fullscreen":
            type_text = "Полный экран"
        elif screenshot_type == "application" and selected_app:
            app_name = selected_app.get('name', 'Unknown')
            app_title = selected_app.get('title', '')
            if app_title:
                type_text = f"Приложение: {app_name} - {app_title}"
            else:
                type_text = f"Приложение: {app_name}"
        else:
            type_text = "Не настроено"
        
        prompt_status = "Настроен" if prompt.strip() else "Не настроен"
        
        return f"Тип: {type_text} | Промпт: {prompt_status}"
    
    def create_widgets(self):
        """Create dialog widgets"""
        theme = self.theme_manager.get_theme()
        
        # Load saved settings
        settings = self.screenshot_settings.get_settings()
        saved_prompt = settings.get("prompt", "Проанализируй этот скриншот максимально подробно на русском языке. Опиши все элементы интерфейса, текст, изображения, цвета, расположение элементов, функциональные кнопки, меню, статусы, ошибки, предупреждения, и любые другие детали. Если это веб-страница - укажи URL, заголовок, содержимое. Если это приложение - опиши его функциональность и текущее состояние. Будь максимально детальным и точным в описании.")
        saved_type = settings.get("screenshot_type", "fullscreen")
        saved_app = settings.get("selected_app")
        
        # Main container with proper layout
        main_container = tk.Frame(self.dialog, bg=theme.colors['bg_primary'])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Content frame (scrollable area)
        content_frame = tk.Frame(main_container, bg=theme.colors['bg_primary'])
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Quick screenshot info
        quick_info_frame = tk.Frame(content_frame, bg=theme.colors['bg_primary'])
        quick_info_frame.pack(fill="x", pady=(0, 15))
        
        quick_info_label = tk.Label(quick_info_frame, text="📷 Настройки быстрого скриншота:", font=theme.fonts['heading'])
        quick_info_label.pack(anchor="w")
        quick_info_label.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_primary'])
        
        # Show current quick screenshot settings
        current_settings = self._get_current_quick_settings_text(settings)
        current_label = tk.Label(quick_info_frame, text=current_settings, font=theme.fonts['message'])
        current_label.pack(anchor="w", pady=(5, 0))
        current_label.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_muted'])
        
        # Prompt input
        prompt_label = tk.Label(content_frame, text="Промпт для анализа:")
        prompt_label.pack(anchor="w", pady=(0, 5))
        prompt_label.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_primary'])
        
        self.prompt_var = tk.StringVar(value=saved_prompt)
        self.prompt_text = tk.Text(content_frame, height=5, wrap=tk.WORD)
        self.prompt_text.pack(fill="x", pady=(0, 20))
        self.prompt_text.insert("1.0", saved_prompt)
        
        # Configure text widget colors
        self.prompt_text.configure(
            bg=theme.colors['input_bg'],
            fg=theme.colors['input_text'],
            font=theme.fonts['message'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=theme.colors['input_focus'],
            highlightbackground=theme.colors['input_border']
        )
        
        # Screenshot options
        options_frame = tk.Frame(content_frame, bg=theme.colors['bg_primary'])
        options_frame.pack(fill="x", pady=(0, 20))
        
        # Options title
        options_title = tk.Label(options_frame, text="Опции скриншота", font=theme.fonts['heading'])
        options_title.pack(anchor="w", pady=(0, 10))
        options_title.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_primary'])
        
        # Full screen option
        self.screenshot_type = tk.StringVar(value=saved_type)
        ttk.Radiobutton(options_frame, text="Полный экран", variable=self.screenshot_type, 
                       value="fullscreen").pack(anchor="w")
        
        # Application selection option
        ttk.Radiobutton(options_frame, text="Выбрать приложение", variable=self.screenshot_type, 
                       value="application").pack(anchor="w")
        
        # Application list (initially hidden)
        self.app_frame = tk.Frame(options_frame, bg=theme.colors['bg_primary'])
        
        # Application list label
        app_label = tk.Label(self.app_frame, text="Выберите приложение:")
        app_label.pack(anchor="w", pady=(0, 5))
        app_label.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_primary'])
        
        # Listbox and scrollbar frame
        listbox_frame = tk.Frame(self.app_frame, bg=theme.colors['bg_primary'])
        listbox_frame.pack(fill="x", expand=False)
        
        self.app_listbox = tk.Listbox(listbox_frame, height=8)
        self.app_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.app_listbox.yview)
        self.app_listbox.configure(yscrollcommand=self.app_scrollbar.set)
        
        # Configure listbox colors
        self.app_listbox.configure(
            bg=theme.colors['input_bg'],
            fg=theme.colors['input_text'],
            font=theme.fonts['primary'],
            selectbackground=theme.colors['sidebar_active'],
            selectforeground=theme.colors['sidebar_active_text']
        )
        
        # Pack listbox and scrollbar
        self.app_listbox.pack(side="left", fill="x", expand=True)
        self.app_scrollbar.pack(side="right", fill="y")
        
        # Bind radio button change
        self.screenshot_type.trace('w', self.toggle_app_selection)
        
        # Show app list if application mode is selected
        if saved_type == "application":
            self.app_frame.pack(fill="x", pady=(10, 0), expand=False)
            self.load_applications()
            if saved_app:
                self.select_saved_app(saved_app)
        
        # Buttons frame (always at bottom)
        self.button_frame = tk.Frame(main_container, bg=theme.colors['bg_primary'])
        self.button_frame.pack(fill="x", pady=(10, 0), side="bottom")
        
        # Create buttons with better spacing
        self.cancel_btn = ttk.Button(self.button_frame, text="Отмена", command=self.cancel, width=15)
        self.cancel_btn.pack(side="right", padx=(0, 10))
        
        self.screenshot_btn = ttk.Button(self.button_frame, text="Сделать скриншот", command=self.take_screenshot, width=20)
        self.screenshot_btn.pack(side="right", padx=(0, 10))
    
    def toggle_app_selection(self, *args):
        """Toggle application selection visibility"""
        self.logger.info(f"Toggle app selection called, current value: {self.screenshot_type.get()}")
        if self.screenshot_type.get() == "application":
            self.logger.info("Showing application list")
            self.app_frame.pack(fill="x", pady=(10, 0), expand=False)
            self.load_applications()
            # Ensure buttons are still visible
            self.logger.info("Ensuring buttons are visible after showing app list")
            self.button_frame.pack(fill="x", pady=(20, 0))
        else:
            self.logger.info("Hiding application list")
            self.app_frame.pack_forget()
            # Ensure buttons are still visible
            self.logger.info("Ensuring buttons are visible after hiding app list")
            self.button_frame.pack(fill="x", pady=(20, 0))
    
    def load_applications(self):
        """Load running applications"""
        try:
            self.logger.info("Loading running applications...")
            apps = self.screenshot_service.get_running_applications()
            self.logger.info(f"Found {len(apps)} applications")
            self.app_listbox.delete(0, tk.END)
            for app in apps:
                # Show window state in the list
                state_text = "📱" if app.get('state') == 'minimized' else "🖥️"
                app_text = f"{state_text} {app['name']} (PID: {app['pid']})"
                if app.get('title'):
                    app_text += f" - {app['title']}"
                self.app_listbox.insert(tk.END, app_text)
                # Use safe logging to avoid encoding issues
                safe_text = app_text.encode('ascii', 'ignore').decode('ascii')
                self.logger.debug(f"Added app to list: {safe_text}")
        except Exception as e:
            self.logger.error(f"Error loading applications: {e}")
            self.app_listbox.insert(tk.END, f"Ошибка: {str(e)}")
    
    def select_saved_app(self, saved_app):
        """Select saved application in the list"""
        try:
            apps = self.screenshot_service.get_running_applications()
            for i, app in enumerate(apps):
                if app['pid'] == saved_app['pid'] and app['name'] == saved_app['name']:
                    self.app_listbox.selection_set(i)
                    self.logger.info(f"Selected saved app: {app['name']} (PID: {app['pid']})")
                    return
            self.logger.warning(f"Saved app not found in current running apps: {saved_app}")
        except Exception as e:
            self.logger.error(f"Ошибка выбора сохраненного приложения: {e}")
    
    def take_screenshot(self):
        """Take screenshot and analyze"""
        try:
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            if not prompt:
                messagebox.showerror("Ошибка", "Пожалуйста, введите запрос для анализа")
                return
            
            screenshot_type = self.screenshot_type.get()
            selected_app = None
            
            # Get selected app info before closing dialog
            if screenshot_type == "application":
                selection = self.app_listbox.curselection()
                if not selection:
                    messagebox.showerror("Ошибка", "Пожалуйста, выберите приложение")
                    return
                
                app_index = selection[0]
                apps = self.screenshot_service.get_running_applications()
                if app_index < len(apps):
                    selected_app = apps[app_index]
                else:
                    messagebox.showerror("Ошибка", "Некорректный выбор приложения")
                    return
            
            # Save settings for future use
            self.screenshot_settings.update_settings(
                screenshot_type=screenshot_type,
                prompt=prompt,
                selected_app=selected_app
            )
            self.logger.info(f"Saved screenshot settings: type={screenshot_type}, app={selected_app}")
            
            # CLOSE DIALOG BEFORE TAKING SCREENSHOT
            self.dialog.destroy()
            
            # Small delay to ensure dialog is fully closed
            import time
            time.sleep(0.1)
            
            if screenshot_type == "fullscreen":
                # Take full screen screenshot
                screenshot_path = self.screenshot_service.capture_full_screen()
            else:
                # Take application screenshot
                screenshot_path = self.screenshot_service.capture_application(
                    selected_app['pid'], 
                    selected_app.get('hwnd')
                )
            
            if screenshot_path:
                # Analyze screenshot
                self.analyze_screenshot(screenshot_path, prompt)
            else:
                messagebox.showerror("Ошибка", "Не удалось сделать скриншот")
                
        except Exception as e:
            self.logger.error(f"Screenshot capture error: {e}")
            messagebox.showerror("Ошибка", f"Скриншот не удался: {str(e)}")
    
    def analyze_screenshot(self, screenshot_path, prompt):
        """Analyze screenshot with AI and integrate into chat context"""
        try:
            # Send screenshot for analysis
            response = self.api_client.analyze_image(screenshot_path, prompt)
            
            if response and response.get("success"):
                analysis = response.get("message", "No analysis received")
                
                # Add analysis to chat as AI message (for display)
                self.chat_widget.add_message(f"Screenshot analysis: {analysis}", "assistant")
                
                # Now automatically send the analysis as a user message to OpenAI chat
                # This creates a proper conversation flow where the user can continue discussing the analysis
                self.logger.info("Sending screenshot analysis to OpenAI chat for context...")
                
                # Send analysis to OpenAI chat in a separate thread
                threading.Thread(target=self._send_analysis_to_chat, args=(analysis,), daemon=True).start()
                
            else:
                # Handle different error types
                error_type = response.get("error", "unknown_error") if response else "no_response"
                error_msg = response.get("message", "Неизвестная ошибка") if response else "Нет ответа от сервера"
                
                if error_type == "unauthorized":
                    # Token expired - need to re-login
                    self.chat_widget.add_message("🔐 Сессия истекла. Необходимо войти заново.", "error")
                    # Trigger re-login in main window
                    self.chat_widget.master.master.show_login_dialog()
                elif error_type == "payment_required":
                    # Payment required - show subscription info
                    self.chat_widget.add_message("💳 Недостаточно средств для анализа изображения.", "error")
                    self.chat_widget.show_subscription_error(response)
                else:
                    # Other errors
                    self.chat_widget.add_message(f"❌ Ошибка анализа: {error_msg}", "error")
                
        except Exception as e:
            self.logger.error(f"Image analysis error: {e}")
            self.chat_widget.add_message(f"Image analysis error: {str(e)}", "error")
    
    def _send_analysis_to_chat(self, analysis):
        """Send screenshot analysis to OpenAI chat for context (runs in separate thread)"""
        try:
            # Get previous response ID for context
            previous_response_id = None
            if self.chat_widget.messages:
                # Find the last AI message with response_id
                for msg in reversed(self.chat_widget.messages):
                    if msg["sender"] == "assistant" and msg.get("response_id"):
                        previous_response_id = msg["response_id"]
                        break
            
            # Send analysis as a user message to OpenAI chat
            message = f"Я проанализировал скриншот. Вот анализ: {analysis}"
            
            self.logger.info(f"Sending analysis to OpenAI chat with context: previous_response_id={previous_response_id}")
            
            # Send to API
            response = self.chat_widget.api_client.send_message(message, previous_response_id)
            
            if response and response.get("success"):
                # Add AI response to chat
                ai_message = response.get("message", "Ответ не получен")
                response_id = response.get("response_id")
                
                # Add message to display
                self.chat_widget.add_message(ai_message, "assistant")
                
                # Update the last message with response_id
                if self.chat_widget.messages and self.chat_widget.messages[-1]["sender"] == "assistant":
                    self.chat_widget.messages[-1]["response_id"] = response_id
                    
                self.logger.info("Screenshot analysis successfully integrated into chat context")
            else:
                error_msg = response.get("error", "Произошла неизвестная ошибка") if response else "Нет ответа от сервера"
                self.chat_widget.add_message(f"Не удалось интегрировать анализ: {error_msg}", "error")
                
        except Exception as e:
            self.logger.error(f"Analysis integration error: {e}")
            self.chat_widget.add_message(f"Ошибка интеграции анализа: {str(e)}", "error")
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()
