"""
Login Dialog - Authentication interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from pathlib import Path
from .themes import ThemeManager
from services.user_preferences import UserPreferencesService

class LoginDialog:
    """Login and registration dialog"""
    
    def __init__(self, parent, api_client):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        self.result = False
        self.theme_manager = ThemeManager()
        self.preferences_service = UserPreferencesService()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Вход / Регистрация")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
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
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Apply theme to dialog
        theme = self.theme_manager.get_theme()
        self.dialog.configure(bg=theme.colors['bg_primary'])
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        theme = self.theme_manager.get_theme()
        
        main_frame = tk.Frame(self.dialog, bg=theme.colors['bg_primary'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="AI Chat Messenger", font=theme.fonts['heading'])
        title_label.pack(pady=(0, 20))
        title_label.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_primary'])
        
        # Mode toggle
        self.is_login_mode = tk.BooleanVar(value=True)
        mode_frame = tk.Frame(main_frame, bg=theme.colors['bg_primary'])
        mode_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Radiobutton(mode_frame, text="Вход", variable=self.is_login_mode, value=True, 
                       command=self.toggle_mode).pack(side="left")
        ttk.Radiobutton(mode_frame, text="Регистрация", variable=self.is_login_mode, value=False, 
                       command=self.toggle_mode).pack(side="left", padx=(20, 0))
        
        # Form fields
        form_frame = tk.Frame(main_frame, bg=theme.colors['bg_primary'])
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Username field
        username_label = tk.Label(form_frame, text="Имя пользователя:")
        username_label.grid(row=0, column=0, sticky="w", pady=5)
        username_label.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_primary'])
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(form_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        self.username_entry.configure(
            bg=theme.colors['input_bg'],
            fg=theme.colors['input_text'],
            font=theme.fonts['primary'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=theme.colors['input_focus'],
            highlightbackground=theme.colors['input_border']
        )
        
        # Password field
        password_label = tk.Label(form_frame, text="Пароль:")
        password_label.grid(row=1, column=0, sticky="w", pady=5)
        password_label.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_primary'])
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(form_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        self.password_entry.configure(
            bg=theme.colors['input_bg'],
            fg=theme.colors['input_text'],
            font=theme.fonts['primary'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=theme.colors['input_focus'],
            highlightbackground=theme.colors['input_border']
        )
        
        # Name field (for registration)
        self.name_label = tk.Label(form_frame, text="Имя:")
        self.name_label.configure(bg=theme.colors['bg_primary'], fg=theme.colors['text_primary'])
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(form_frame, textvariable=self.name_var, width=30)
        self.name_entry.configure(
            bg=theme.colors['input_bg'],
            fg=theme.colors['input_text'],
            font=theme.fonts['primary'],
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=theme.colors['input_focus'],
            highlightbackground=theme.colors['input_border']
        )
        
        # Configure grid weights
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Remember me checkbox (only for login mode)
        self.remember_me_var = tk.BooleanVar()
        self.remember_me_checkbox = ttk.Checkbutton(
            form_frame, 
            text="Запомнить меня", 
            variable=self.remember_me_var
        )
        self.remember_me_checkbox.grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=theme.colors['bg_primary'])
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.submit_button = ttk.Button(button_frame, text="Войти", command=self.submit)
        self.submit_button.pack(side="right", padx=(10, 0))
        
        ttk.Button(button_frame, text="Отмена", command=self.cancel).pack(side="right")
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.submit())
        self.username_entry.focus()
        
        # Initial mode setup
        self.toggle_mode()
        
        # Load saved login data
        self.load_saved_login_data()
    
    def toggle_mode(self):
        """Toggle between login and registration mode"""
        if self.is_login_mode.get():
            # Login mode
            self.name_label.grid_remove()
            self.name_entry.grid_remove()
            self.remember_me_checkbox.grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
            self.submit_button.config(text="Войти")
            self.dialog.title("Вход")
        else:
            # Registration mode
            self.remember_me_checkbox.grid_remove()
            self.name_label.grid(row=2, column=0, sticky="w", pady=5)
            self.name_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))
            self.submit_button.config(text="Зарегистрироваться")
            self.dialog.title("Регистрация")
    
    def load_saved_login_data(self):
        """Load saved login data if available"""
        try:
            saved_data = self.preferences_service.load_login_data()
            if saved_data:
                self.username_var.set(saved_data.get("username", ""))
                self.password_var.set(saved_data.get("password", ""))
                self.remember_me_var.set(saved_data.get("remember_me", False))
                self.logger.info("Loaded saved login data")
        except Exception as e:
            self.logger.error(f"Error loading saved login data: {e}")
    
    def submit(self):
        """Submit login or registration"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все обязательные поля")
            return
        
        if not self.is_login_mode.get():
            # Registration
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Пожалуйста, введите ваше имя")
                return
            
            try:
                result = self.api_client.register(username, password, username)  # Используем username как email
                if result.get("success"):
                    messagebox.showinfo("Успех", result.get("message", "Регистрация прошла успешно! Теперь вы можете войти."))
                    self.is_login_mode.set(True)
                    self.toggle_mode()
                else:
                    messagebox.showerror("Ошибка", result.get("message", "Регистрация не удалась. Попробуйте еще раз."))
            except Exception as e:
                self.logger.error(f"Registration error: {e}")
                messagebox.showerror("Ошибка", f"Регистрация не удалась: {str(e)}")
        else:
            # Login
            try:
                result = self.api_client.login(username, password)
                if result.get("success"):
                    # Successful login - save data if remember me is checked
                    remember_me = self.remember_me_var.get()
                    self.preferences_service.save_login_data(username, password, remember_me)
                    
                    self.result = True
                    self.dialog.destroy()
                elif result.get("error") == "invalid_credentials":
                    # Invalid credentials
                    messagebox.showerror("Ошибка входа", result.get("message", "Неверное имя пользователя или пароль"))
                elif result.get("error") == "payment_required":
                    # Payment required - show subscription dialog
                    self.show_subscription_dialog(result)
                else:
                    # Other errors
                    messagebox.showerror("Ошибка", result.get("message", "Ошибка входа. Попробуйте еще раз."))
            except Exception as e:
                self.logger.error(f"Login error: {e}")
                messagebox.showerror("Ошибка", f"Ошибка входа: {str(e)}")
    
    def show_subscription_dialog(self, login_result):
        """Show subscription dialog when payment is required"""
        from .subscription_dialog import SubscriptionDialog
        
        # Create subscription dialog
        subscription_dialog = SubscriptionDialog(
            self.dialog, 
            login_result.get("subscription_status", {}),
            login_result.get("available_plans", []),
            login_result.get("credit_packages", []),
            login_result.get("purchase_url", "")
        )
        
        # Wait for dialog result
        self.dialog.wait_window(subscription_dialog.dialog)
        
        # If user purchased subscription, try login again
        if subscription_dialog.result == "purchased":
            # Close login dialog and let main app handle re-login
            self.result = "subscription_purchased"
            self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()
