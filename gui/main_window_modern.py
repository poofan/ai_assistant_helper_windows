"""
Modern Main Window using CustomTkinter for contemporary design
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import logging
from pathlib import Path

from .login_dialog_modern import ModernLoginDialog
from .chat_widget_modern import ModernChatWidget
from .themes import ThemeManager
from services.api_client import APIClient
from services.screenshot import ScreenshotService
from services.chat_manager import ChatManager
from services.coordinates_manager import CoordinatesManager

class ModernMainWindow(ctk.CTk):
    """Modern main application window using CustomTkinter"""
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.api_client = APIClient(config)
        self.screenshot_service = ScreenshotService()
        self.chat_manager = ChatManager()
        self.theme_manager = ThemeManager()
        self.coordinates_manager = CoordinatesManager()
        
        # GUI state
        self.is_authenticated = False
        self.current_chat_id = None
        self.sidebar_width = 300
        
        # Load sidebar state from config
        self.sidebar_visible = config.getboolean('gui', 'sidebar_visible', True)
        
        # Setup window
        self.setup_window()
        self.create_widgets()
        
        # Check authentication
        self.check_authentication()
    
    def setup_window(self):
        """Setup main window properties"""
        self.title("🤖 AI Чат Помощник - Modern")
        
        # Set initial window size based on sidebar state
        if self.sidebar_visible:
            self.geometry("1100x800")  # Increased height for better chat visibility
        else:
            self.geometry("750x800")  # Increased height for better chat visibility
        
        # Set minimum window size
        self.minsize(800, 600)
        
        # Configure CustomTkinter
        ctk.set_appearance_mode("light")  # Will be changed by theme manager
        ctk.set_default_color_theme("blue")
        
        # Set window icon if available
        try:
            icon_path = Path("images/logo.ico")
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception as e:
            self.logger.warning(f"Could not load icon: {e}")
    
    def create_widgets(self):
        """Create main application widgets"""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid weights
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create chat area
        self.create_chat_area()
        
        # Apply theme
        self.apply_theme()
    
    def create_sidebar(self):
        """Create completely independent sidebar with proper chat list"""
        self.sidebar = ctk.CTkFrame(self.main_frame, width=self.sidebar_width)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.sidebar.grid_propagate(False)
        
        # Use pack layout for better control
        # Sidebar header (fixed at top)
        header_label = ctk.CTkLabel(
            self.sidebar,
            text="💬 Чаты",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(fill="x", pady=(15, 10), padx=10)
        
        # Chat list area - completely independent
        self.chat_list_frame = ctk.CTkFrame(self.sidebar)
        self.chat_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create scrollable frame for chats with fixed height
        self.chat_scroll_frame = ctk.CTkScrollableFrame(
            self.chat_list_frame,
            fg_color="transparent",
            height=400  # Reduced height to make room for buttons
        )
        self.chat_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store chat buttons for easy management
        self.chat_buttons = []
        
        # Sidebar buttons (fixed at bottom)
        button_frame = ctk.CTkFrame(self.sidebar)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.logger.info("Button frame created and packed in sidebar")
        
        # New chat button
        new_chat_btn = ctk.CTkButton(
            button_frame,
            text="➕ Новый чат",
            command=self.create_new_chat,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        new_chat_btn.pack(fill="x", pady=(10, 5))
        self.logger.info("New chat button created and packed")
        
        # Edit chat button
        self.edit_chat_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Редактировать",
            command=self.edit_current_chat,
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color="#17a2b8",
            hover_color="#138496",
            state="disabled"  # Initially disabled
        )
        self.edit_chat_btn.pack(fill="x", pady=5)
        self.logger.info("Edit chat button created and packed")
        
        # Delete chat button
        self.delete_chat_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Удалить",
            command=self.delete_current_chat,
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"  # Initially disabled
        )
        self.delete_chat_btn.pack(fill="x", pady=5)
        self.logger.info("Delete chat button created and packed")
        
        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            button_frame,
            text="🌙 Темная тема",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.theme_btn.pack(fill="x", pady=5)
        self.logger.info("Theme button created and packed")
        
        # Coordinates button removed - now in screenshot settings dialog
        
        # Logout button
        logout_btn = ctk.CTkButton(
            button_frame,
            text="🚪 Выйти",
            command=self.logout,
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        logout_btn.pack(fill="x", pady=(5, 10))
        self.logger.info("Logout button created and packed")
        
        # Load chats into sidebar
        self.load_chats_to_sidebar()
        
        # Hide sidebar if needed
        if not self.sidebar_visible:
            self.sidebar.grid_remove()
    
    def create_chat_area(self):
        """Create modern chat area"""
        # Top panel with sidebar toggle
        top_panel = ctk.CTkFrame(self.main_frame, height=50)
        top_panel.grid(row=0, column=1, sticky="ew", pady=(0, 5))
        top_panel.grid_propagate(False)
        
        # Sidebar toggle button
        self.sidebar_toggle_btn = ctk.CTkButton(
            top_panel,
            text="✕" if self.sidebar_visible else "☰",
            command=self.toggle_sidebar,
            font=ctk.CTkFont(size=14),
            width=40,
            height=40
        )
        self.sidebar_toggle_btn.pack(side="left", padx=10, pady=5)
        
        # Chat title
        self.chat_title = ctk.CTkLabel(
            top_panel,
            text="💬 AI Чат Помощник",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.chat_title.pack(side="left", padx=10, pady=5)
        
        # Chat frame
        self.chat_frame = ctk.CTkFrame(self.main_frame)
        self.chat_frame.grid(row=1, column=1, sticky="nsew", pady=(0, 5))
        
        # Configure chat frame grid
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        
        # Create modern chat widget
        from .chat_widget_modern import ModernChatWidget
        self.chat_widget = ModernChatWidget(
            self.chat_frame,
            self.api_client,
            self.screenshot_service,
            self.chat_manager,
            self.theme_manager
        )
        self.chat_widget.grid(row=0, column=0, sticky="nsew")
    
    def apply_theme(self):
        """Apply theme to all widgets"""
        # This will be implemented to work with CustomTkinter
        pass
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility with adaptive window sizing"""
        current_width = self.winfo_width()
        current_height = self.winfo_height()
        
        if self.sidebar_visible:
            # Hide sidebar and shrink window
            self.sidebar.grid_remove()
            self.sidebar_visible = False
            self.sidebar_toggle_btn.configure(text="☰")
            
            # Calculate new window size
            new_width = max(600, current_width - self.sidebar_width)
            new_height = max(600, current_height)  # Ensure minimum height
            self.geometry(f"{new_width}x{new_height}")
            
            # Save state to config
            self.config.set('gui', 'sidebar_visible', 'false')
            self.config.save_config()
            
            self.logger.info(f"Sidebar hidden, window resized to {new_width}x{current_height}")
        else:
            # Show sidebar and expand window
            self.sidebar.grid()
            self.sidebar_visible = True
            self.sidebar_toggle_btn.configure(text="✕")
            
            # Calculate new window size
            new_width = current_width + self.sidebar_width
            new_height = max(600, current_height)  # Ensure minimum height
            self.geometry(f"{new_width}x{new_height}")
            
            # Save state to config
            self.config.set('gui', 'sidebar_visible', 'true')
            self.config.save_config()
            
            self.logger.info(f"Sidebar shown, window resized to {new_width}x{current_height}")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "light":
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀️ Светлая тема")
        else:
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙 Темная тема")
    
    def create_new_chat(self):
        """Create a new chat"""
        if self.chat_widget:
            self.chat_widget.create_new_chat()
            # Force sidebar update after creating new chat
            self.load_chats_to_sidebar()
    
    def load_chats_to_sidebar(self):
        """Load chats into sidebar with modern buttons"""
        try:
            # Clear existing chat buttons
            for button in self.chat_buttons:
                button.destroy()
            self.chat_buttons.clear()
            
            # Get all chats
            chats = self.chat_manager.get_all_chats()
            
            if chats:
                for chat_id, chat_data in chats.items():
                    chat_name = chat_data.get("name", f"Чат {chat_id[:8]}")
                    self.create_chat_button(chat_id, chat_name)
                
                # Update button states based on current chat
                if hasattr(self, 'chat_widget') and self.chat_widget and hasattr(self.chat_widget, 'current_chat_id'):
                    self.update_chat_buttons_state(self.chat_widget.current_chat_id)
            else:
                # Show "no chats" message
                no_chats_label = ctk.CTkLabel(
                    self.chat_scroll_frame,
                    text="Нет чатов",
                    font=ctk.CTkFont(size=12),
                    text_color="#6c757d"
                )
                no_chats_label.pack(pady=10)
                self.chat_buttons.append(no_chats_label)
                
        except Exception as e:
            self.logger.error(f"Error loading chats to sidebar: {e}")
            error_label = ctk.CTkLabel(
                self.chat_scroll_frame,
                text="Ошибка загрузки чатов",
                font=ctk.CTkFont(size=12),
                text_color="#dc3545"
            )
            error_label.pack(pady=10)
            self.chat_buttons.append(error_label)
    
    def create_chat_button(self, chat_id, chat_name):
        """Create a modern chat button"""
        # Create chat button with modern styling
        chat_button = ctk.CTkButton(
            self.chat_scroll_frame,
            text=f"💬 {chat_name}",
            command=lambda: self.select_chat(chat_id),
            font=ctk.CTkFont(size=13),
            height=45,
            fg_color="transparent",
            hover_color="#e9ecef",
            text_color="#212529",
            anchor="w"
        )
        chat_button.pack(fill="x", pady=3, padx=8)
        self.chat_buttons.append(chat_button)
        
        # Store chat_id for reference
        chat_button.chat_id = chat_id
        
        # Add right-click context menu
        chat_button.bind("<Button-3>", lambda e, cid=chat_id: self.show_chat_context_menu(e, cid))
    
    def select_chat(self, chat_id):
        """Select a chat"""
        if self.chat_widget:
            # Update visual selection
            self.update_chat_selection(chat_id)
            
            # Switch to chat
            self.chat_widget.set_current_chat(chat_id)
            
            # Update button states
            self.update_chat_buttons_state(chat_id)
            
            self.logger.info(f"Selected chat: {chat_id}")
    
    def update_chat_selection(self, selected_chat_id):
        """Update visual selection of chat buttons"""
        for button in self.chat_buttons:
            if hasattr(button, 'chat_id'):
                if button.chat_id == selected_chat_id:
                    # Highlight selected chat
                    button.configure(
                        fg_color="#007bff",
                        text_color="white",
                        hover_color="#0056b3"
                    )
                else:
                    # Reset other chats
                    button.configure(
                        fg_color="transparent",
                        text_color="#212529",
                        hover_color="#e9ecef"
                    )
    
    def update_chat_buttons_state(self, chat_id):
        """Update the state of edit and delete buttons based on selected chat"""
        try:
            if chat_id and chat_id != "welcome_chat":  # Don't allow editing/deleting welcome chat
                # Enable buttons
                self.edit_chat_btn.configure(state="normal")
                self.delete_chat_btn.configure(state="normal")
            else:
                # Disable buttons for welcome chat or no selection
                self.edit_chat_btn.configure(state="disabled")
                self.delete_chat_btn.configure(state="disabled")
        except Exception as e:
            self.logger.error(f"Error updating chat buttons state: {e}")
    
    def show_chat_context_menu(self, event, chat_id):
        """Show context menu for chat"""
        try:
            from tkinter import messagebox, simpledialog
            
            # Create context menu
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(
                label="✏️ Переименовать",
                command=lambda: self.rename_chat(chat_id)
            )
            context_menu.add_command(
                label="🗑️ Удалить",
                command=lambda: self.delete_chat(chat_id)
            )
            
            # Show context menu
            context_menu.tk_popup(event.x_root, event.y_root)
            
        except Exception as e:
            self.logger.error(f"Error showing context menu: {e}")
    
    def rename_chat(self, chat_id):
        """Rename a chat"""
        try:
            from tkinter import simpledialog
            
            current_name = self.chat_manager.get_chat(chat_id).get("name", "")
            new_name = simpledialog.askstring(
                "Переименовать чат",
                "Введите новое название:",
                initialvalue=current_name
            )
            
            if new_name and new_name.strip():
                self.chat_manager.update_chat_name(chat_id, new_name.strip())
                self.load_chats_to_sidebar()
                self.logger.info(f"Renamed chat {chat_id} to {new_name}")
                
        except Exception as e:
            self.logger.error(f"Error renaming chat: {e}")
    
    def delete_chat(self, chat_id):
        """Delete a chat"""
        try:
            from tkinter import messagebox
            
            result = messagebox.askyesno(
                "Удалить чат",
                "Вы уверены, что хотите удалить этот чат? Это действие нельзя отменить."
            )
            
            if result:
                self.chat_manager.delete_chat(chat_id)
                self.load_chats_to_sidebar()
                self.logger.info(f"Deleted chat {chat_id}")
                
        except Exception as e:
            self.logger.error(f"Error deleting chat: {e}")
    
    def edit_current_chat(self):
        """Edit the currently selected chat"""
        try:
            if hasattr(self.chat_widget, 'current_chat_id') and self.chat_widget.current_chat_id:
                self.rename_chat(self.chat_widget.current_chat_id)
            else:
                from tkinter import messagebox
                messagebox.showwarning("Предупреждение", "Сначала выберите чат для редактирования")
        except Exception as e:
            self.logger.error(f"Error editing current chat: {e}")
    
    def delete_current_chat(self):
        """Delete the currently selected chat"""
        try:
            if hasattr(self.chat_widget, 'current_chat_id') and self.chat_widget.current_chat_id:
                self.delete_chat(self.chat_widget.current_chat_id)
            else:
                from tkinter import messagebox
                messagebox.showwarning("Предупреждение", "Сначала выберите чат для удаления")
        except Exception as e:
            self.logger.error(f"Error deleting current chat: {e}")
    
    def check_authentication(self):
        """Check if user is authenticated"""
        if self.api_client.auth_token:
            # Verify token
            result = self.api_client.verify_token()
            if result.get("success"):
                self.is_authenticated = True
                self.logger.info("Token is valid, user is authenticated")
            else:
                self.logger.warning("Token verification failed")
                self.show_login_dialog()
        else:
            self.logger.info("No auth token found")
            self.show_login_dialog()
    
    def show_login_dialog(self):
        """Show login dialog"""
        from .login_dialog_modern import ModernLoginDialog
        login_dialog = ModernLoginDialog(self, self.api_client, self.theme_manager)
        if login_dialog.result:
            self.is_authenticated = True
            self.logger.info("User authenticated successfully")
        else:
            self.logger.info("Authentication cancelled")
            self.quit()
    
    def logout(self):
        """Logout user"""
        self.api_client.logout()
        self.is_authenticated = False
        self.logger.info("User logged out")
        self.show_login_dialog()
    
    # Coordinates dialog methods removed - now in screenshot settings dialog
    
    def run(self):
        """Start the application"""
        self.logger.info("Starting main application loop")
        self.mainloop()
