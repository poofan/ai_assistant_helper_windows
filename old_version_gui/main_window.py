"""
Main Window - Primary GUI interface for the AI Chat Messenger
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import threading
import logging
from pathlib import Path

from .login_dialog import LoginDialog
from .chat_widget import ChatWidget
from .themes import ThemeManager
from services.api_client import APIClient
from services.screenshot import ScreenshotService
from services.chat_manager import ChatManager

class MainWindow:
    """Main application window"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.api_client = APIClient(config)
        self.screenshot_service = ScreenshotService()
        self.chat_manager = ChatManager()
        self.theme_manager = ThemeManager()
        
        # GUI state
        self.is_authenticated = False
        self.current_chat_id = None
        self.sidebar_width = 250  # Approximate sidebar width
        
        # Load sidebar state from config
        self.sidebar_visible = config.getboolean('gui', 'sidebar_visible', True)
        
        # Create main window
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("AI Чат Помощник")
        
        # Set initial window size based on sidebar state
        if self.sidebar_visible:
            self.root.geometry("1000x700")
        else:
            # Smaller window when sidebar is hidden
            self.root.geometry("750x700")
        
        self.root.minsize(600, 400)
        
        # Set application icon
        try:
            icon_path = Path("images") / "logo.png"
            if icon_path.exists():
                # Load and set icon
                icon_image = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon_image)
                self.logger.info(f"Application icon loaded from {icon_path}")
            else:
                self.logger.warning(f"Icon file not found: {icon_path}")
        except Exception as e:
            self.logger.error(f"Failed to load application icon: {e}")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar - fixed width
        self.root.grid_columnconfigure(1, weight=1)  # Chat area - flexible
        
        # Apply initial theme to main window only
        theme = self.theme_manager.get_theme()
        self.root.configure(bg=theme.colors['bg_primary'])
        
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Sidebar for chat list
        self.create_sidebar()
        
        # Main chat area
        self.create_chat_area()
        
        # Apply theme to all widgets after they are created
        self.apply_theme(self.theme_manager.current_theme)
        
        # Load existing chats after all widgets are created
        self.load_chats()
        
        # Check if user is already authenticated
        if self.check_authentication():
            self.is_authenticated = True
            self.logger.info("User already authenticated")
        else:
            # Show login dialog if not authenticated
            self.show_login_dialog()
    
    def create_sidebar(self):
        """Create sidebar with chat list"""
        theme = self.theme_manager.get_theme()
        
        self.sidebar = tk.Frame(self.root, width=250, bg=theme.colors['sidebar_bg'])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Initialize sidebar state based on config
        if not self.sidebar_visible:
            self.sidebar.grid_remove()
        
        # Chat list header
        header_label = tk.Label(self.sidebar, text="💬 Чаты", font=theme.fonts['heading'])
        header_label.pack(pady=(5, 5))
        header_label.configure(bg=theme.colors['sidebar_bg'], fg=theme.colors['sidebar_text'])
        
        # Chat listbox with scrollbar
        list_frame = tk.Frame(self.sidebar, bg=theme.colors['sidebar_bg'])
        list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        self.chat_listbox = tk.Listbox(list_frame)
        chat_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.chat_listbox.yview)
        self.chat_listbox.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_listbox.pack(side="left", fill="both", expand=True)
        chat_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.chat_listbox.bind('<<ListboxSelect>>', self.on_chat_select)
        
        # Bind double-click to rename
        self.chat_listbox.bind('<Double-Button-1>', self.on_chat_double_click)
        
        # Bind right-click for context menu
        self.chat_listbox.bind('<Button-3>', self.on_chat_right_click)
        
        # Chat management buttons
        button_frame = tk.Frame(self.sidebar, bg=theme.colors['sidebar_bg'])
        button_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        ttk.Button(button_frame, text="➕ Новый чат", command=self.create_new_chat).pack(side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(button_frame, text="✏️ Переименовать", command=self.rename_chat).pack(side="left", fill="x", expand=True, padx=(2, 2))
        ttk.Button(button_frame, text="🗑️ Удалить", command=self.delete_chat).pack(side="right", fill="x", expand=True, padx=(2, 0))
        
        # Theme toggle button
        ttk.Button(self.sidebar, text="🌙 Темная тема", command=self.toggle_theme).pack(padx=5, pady=(0, 5), fill="x")
        
        # Logout button
        ttk.Button(self.sidebar, text="🚪 Выйти", command=self.logout).pack(padx=5, pady=(0, 5), fill="x")
    
    def create_chat_area(self):
        """Create main chat area"""
        theme = self.theme_manager.get_theme()
        self.chat_frame = tk.Frame(self.root, bg=theme.colors['bg_primary'])
        self.chat_frame.grid(row=0, column=1, sticky="nsew")
        self.chat_frame.grid_rowconfigure(1, weight=1)  # Chat widget gets weight 1
        self.chat_frame.grid_columnconfigure(0, weight=1)
        
        # Top panel with sidebar toggle button
        top_panel = tk.Frame(self.chat_frame, bg=theme.colors['bg_primary'], height=30)
        top_panel.grid(row=0, column=0, sticky="ew")
        top_panel.grid_propagate(False)  # Keep fixed height
        
        # Sidebar toggle button
        toggle_text = "✕" if self.sidebar_visible else "☰"
        self.sidebar_toggle_btn = ttk.Button(
            top_panel, 
            text=toggle_text, 
            command=self.toggle_sidebar,
            width=3
        )
        self.sidebar_toggle_btn.pack(side="left", padx=5, pady=2)
        
        # Chat widget
        self.chat_widget = ChatWidget(self.chat_frame, self.api_client, self.screenshot_service, self.chat_manager, self)
        self.chat_widget.grid(row=1, column=0, sticky="nsew")
    
    def check_authentication(self):
        """Check if user is already authenticated with valid token"""
        try:
            # Try to load saved token
            if self.api_client.load_auth_token():
                # Verify token with server
                result = self.api_client.verify_token()
                if result.get("success"):
                    self.logger.info("Token is valid, user is authenticated")
                    return True
                else:
                    self.logger.info("Token is invalid, clearing saved token")
                    self.api_client.logout()
                    return False
            else:
                self.logger.info("No saved token found")
                return False
        except Exception as e:
            self.logger.error(f"Authentication check failed: {e}")
            return False
    
    def show_login_dialog(self):
        """Show login/registration dialog"""
        login_dialog = LoginDialog(self.root, self.api_client)
        self.root.wait_window(login_dialog.dialog)
        
        if login_dialog.result == True:
            self.is_authenticated = True
            self.logger.info("User authenticated successfully")
            self.load_chats()
        elif login_dialog.result == "subscription_purchased":
            # User purchased subscription, try to login again
            self.logger.info("User purchased subscription, attempting re-login")
            messagebox.showinfo("Подписка", "Подписка активирована! Попробуйте войти снова.")
            self.show_login_dialog()  # Recursive call to try login again
        else:
            self.logger.info("Authentication cancelled")
            self.root.destroy()
            exit(0)
    
    def create_new_chat(self):
        """Create a new chat"""
        if not self.is_authenticated:
            messagebox.showwarning("Ошибка", "Необходимо войти в систему для создания чата")
            self.show_login_dialog()
            return
        
        import uuid
        chat_id = f"chat_{uuid.uuid4().hex[:8]}"
        chat_name = f"Chat {len(self.chat_manager.get_all_chats()) + 1}"
        
        # Create chat in manager
        self.chat_manager.create_chat(chat_id, chat_name)
        
        # Update UI
        self.load_chats()
        self.current_chat_id = chat_id
        
        # Clear chat widget
        self.chat_widget.clear_chat()
        self.chat_widget.set_current_chat(chat_id)
        
        # Select the new chat
        self.select_chat_by_id(chat_id)
        
        self.logger.info(f"Created new chat: {chat_id} - {chat_name}")
    
    def load_chats(self):
        """Load existing chats from ChatManager"""
        self.chat_listbox.delete(0, tk.END)
        
        chat_list = self.chat_manager.get_chat_list()
        
        if not chat_list:
            # Create welcome chat if no chats exist
            welcome_id = "welcome_chat"
            self.chat_manager.create_chat(welcome_id, "Welcome Chat")
            chat_list = self.chat_manager.get_chat_list()
        
        for chat in chat_list:
            self.chat_listbox.insert(tk.END, chat["name"])
        
        # Select first chat if none selected
        if not self.current_chat_id and chat_list:
            self.current_chat_id = chat_list[0]["id"]
            self.chat_listbox.selection_set(0)
            self.chat_widget.set_current_chat(self.current_chat_id)
            self.load_chat_messages(self.current_chat_id)
    
    def on_chat_select(self, event):
        """Handle chat selection"""
        selection = self.chat_listbox.curselection()
        if selection:
            index = selection[0]
            chat_list = self.chat_manager.get_chat_list()
            if index < len(chat_list):
                chat_id = chat_list[index]["id"]
                self.current_chat_id = chat_id
                self.chat_widget.set_current_chat(chat_id)
                self.load_chat_messages(chat_id)
                self.logger.info(f"Selected chat: {chat_id}")
    
    def on_chat_double_click(self, event):
        """Handle double-click on chat to rename"""
        self.rename_chat()
    
    def on_chat_right_click(self, event):
        """Handle right-click on chat to show context menu"""
        # Select the item under the cursor
        index = self.chat_listbox.nearest(event.y)
        if index >= 0:
            self.chat_listbox.selection_clear(0, tk.END)
            self.chat_listbox.selection_set(index)
            self.chat_listbox.activate(index)
            
            # Show context menu
            self.show_chat_context_menu(event.x_root, event.y_root)
    
    def show_chat_context_menu(self, x, y):
        """Show context menu for chat"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="✏️ Переименовать", command=self.rename_chat)
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Удалить", command=self.delete_chat)
        
        try:
            context_menu.tk_popup(x, y)
        finally:
            context_menu.grab_release()
    
    def select_chat_by_id(self, chat_id):
        """Select chat by ID in the listbox"""
        chat_list = self.chat_manager.get_chat_list()
        for i, chat in enumerate(chat_list):
            if chat["id"] == chat_id:
                self.chat_listbox.selection_clear(0, tk.END)
                self.chat_listbox.selection_set(i)
                self.chat_listbox.see(i)
                break
    
    def load_chat_messages(self, chat_id):
        """Load messages for the selected chat"""
        messages = self.chat_manager.get_messages(chat_id)
        self.chat_widget.load_messages(messages)
    
    def rename_chat(self):
        """Rename selected chat"""
        if not self.is_authenticated:
            messagebox.showwarning("Ошибка", "Необходимо войти в систему для переименования чата")
            self.show_login_dialog()
            return
            
        selection = self.chat_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a chat to rename")
            return
        
        index = selection[0]
        chat_list = self.chat_manager.get_chat_list()
        if index >= len(chat_list):
            return
        
        chat = chat_list[index]
        current_name = chat["name"]
        
        # Show rename dialog
        new_name = tk.simpledialog.askstring(
            "Переименовать чат", 
            f"Введите новое имя для чата:",
            initialvalue=current_name
        )
        
        if new_name and new_name.strip() and new_name.strip() != current_name:
            new_name = new_name.strip()
            
            # Update in manager
            self.chat_manager.update_chat_name(chat["id"], new_name)
            
            # Reload chat list to show updated name
            self.load_chats()
            
            # Reselect the renamed chat
            self.select_chat_by_id(chat["id"])
            
            self.logger.info(f"Renamed chat: '{current_name}' -> '{new_name}'")
        elif new_name and new_name.strip() == current_name:
            # Name unchanged, do nothing
            pass
        else:
            # User cancelled or entered empty name
            pass
    
    def delete_chat(self):
        """Delete selected chat"""
        if not self.is_authenticated:
            messagebox.showwarning("Ошибка", "Необходимо войти в систему для удаления чата")
            self.show_login_dialog()
            return
            
        selection = self.chat_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a chat to delete")
            return
        
        index = selection[0]
        chat_list = self.chat_manager.get_chat_list()
        if index >= len(chat_list):
            return
        
        chat = chat_list[index]
        
        # Confirm deletion
        if messagebox.askyesno("Подтверждение удаления", f"Вы уверены, что хотите удалить '{chat['name']}'?"):
            self.chat_manager.delete_chat(chat["id"])
            
            # If we deleted the current chat, clear the chat widget
            if self.current_chat_id == chat["id"]:
                self.current_chat_id = None
                self.chat_widget.clear_chat()
            
            # Reload chat list
            self.load_chats()
            
            self.logger.info(f"Deleted chat: {chat['id']} - {chat['name']}")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.logger.info("Toggle theme button clicked")
        current_theme = self.theme_manager.current_theme
        new_theme = 'dark' if current_theme == 'light' else 'light'
        
        self.logger.info(f"Current theme: {current_theme}, switching to: {new_theme}")
        
        if self.theme_manager.set_theme(new_theme):
            self.logger.info(f"Switched to {new_theme} theme")
            self.apply_theme(new_theme)
        else:
            self.logger.error("Failed to switch theme")
    
    def apply_theme(self, theme_name):
        """Apply theme to all widgets"""
        theme = self.theme_manager.get_theme(theme_name)
        
        # Apply to main window
        self.root.configure(bg=theme.colors['bg_primary'])
        
        # Apply to sidebar if it exists
        if hasattr(self, 'sidebar'):
            self.apply_sidebar_theme(theme)
        
        # Apply to chat widget if it exists
        if hasattr(self, 'chat_widget'):
            self.chat_widget.apply_theme(theme)
        
        # Apply to chat frame if it exists
        if hasattr(self, 'chat_frame'):
            self.chat_frame.configure(bg=theme.colors['bg_primary'])
        
        # Update theme button text if sidebar exists
        if hasattr(self, 'sidebar'):
            self.update_theme_button(theme_name)
        
        self.logger.info(f"Applied {theme_name} theme to all widgets")
    
    def apply_sidebar_theme(self, theme):
        """Apply theme to sidebar and all its widgets"""
        # Apply to sidebar frame
        self.sidebar.configure(bg=theme.colors['sidebar_bg'])
        
        # Apply to all child widgets
        self.apply_widget_theme(self.sidebar, theme)
    
    def apply_widget_theme(self, parent, theme):
        """Recursively apply theme to all child widgets"""
        for child in parent.winfo_children():
            widget_type = child.winfo_class()
            
            if widget_type == 'Frame':
                child.configure(bg=theme.colors['sidebar_bg'])
            elif widget_type == 'TFrame':
                # ttk.Frame doesn't support bg, skip
                pass
            elif widget_type == 'Label':
                child.configure(bg=theme.colors['sidebar_bg'], fg=theme.colors['sidebar_text'])
            elif widget_type == 'TLabel':
                # ttk.Label styling is more complex, we'll handle it separately
                pass
            elif widget_type == 'Listbox':
                child.configure(
                    bg=theme.colors['input_bg'],
                    fg=theme.colors['input_text'],
                    selectbackground=theme.colors['sidebar_active'],
                    selectforeground=theme.colors['sidebar_active_text'],
                    font=theme.fonts['primary']
                )
            elif widget_type == 'TButton':
                # ttk.Button styling is more complex, we'll handle it separately
                pass
            
            # Recursively apply to children
            if hasattr(child, 'winfo_children'):
                self.apply_widget_theme(child, theme)
    
    def update_theme_button(self, theme_name):
        """Update theme toggle button text"""
        theme_button = None
        for child in self.sidebar.winfo_children():
            if isinstance(child, ttk.Button) and ("🌙" in child.cget("text") or "☀️" in child.cget("text")):
                theme_button = child
                break
        
        if theme_button:
            theme_button.configure(text="☀️ Light" if theme_name == 'light' else "🌙 Dark")
    
    def logout(self):
        """Logout user"""
        self.is_authenticated = False
        self.api_client.logout()
        self.chat_listbox.delete(0, tk.END)
        self.chat_widget.clear_chat()
        self.show_login_dialog()
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility with adaptive window sizing"""
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        if self.sidebar_visible:
            # Hide sidebar and shrink window
            self.sidebar.grid_remove()
            self.sidebar_visible = False
            self.sidebar_toggle_btn.configure(text="☰")
            
            # Calculate new window size (subtract sidebar width)
            new_width = max(600, current_width - self.sidebar_width)  # Minimum width 600
            self.root.geometry(f"{new_width}x{current_height}")
            
            # Save state to config
            self.config.set('gui', 'sidebar_visible', 'false')
            self.config.save_config()
            
            self.logger.info(f"Sidebar hidden, window resized to {new_width}x{current_height}")
        else:
            # Show sidebar and expand window
            self.sidebar.grid()
            self.sidebar_visible = True
            self.sidebar_toggle_btn.configure(text="✕")
            
            # Calculate new window size (add sidebar width)
            new_width = current_width + self.sidebar_width
            self.root.geometry(f"{new_width}x{current_height}")
            
            # Save state to config
            self.config.set('gui', 'sidebar_visible', 'true')
            self.config.save_config()
            
            self.logger.info(f"Sidebar shown, window resized to {new_width}x{current_height}")
    
    def run(self):
        """Start the main application loop"""
        self.logger.info("Starting main application loop")
        self.root.mainloop()
