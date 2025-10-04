"""
Modern Login Dialog using CustomTkinter for contemporary design
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging

class ModernLoginDialog(ctk.CTkToplevel):
    """Modern login dialog using CustomTkinter"""
    
    def __init__(self, parent, api_client, theme_manager):
        super().__init__(parent)
        
        self.api_client = api_client
        self.theme_manager = theme_manager
        self.logger = logging.getLogger(__name__)
        
        # Dialog state
        self.result = False
        
        # Setup dialog
        self.setup_dialog()
        self.create_widgets()
        
        # Center dialog
        self.center_dialog()
    
    def setup_dialog(self):
        """Setup dialog properties"""
        self.title("🔐 Вход в систему")
        self.geometry("450x650")
        self.resizable(True, True)
        self.minsize(400, 600)
        
        # Make dialog modal
        self.transient(self.master)
        self.grab_set()
        
        # Configure CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
    
    def create_widgets(self):
        """Create modern login widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="🤖 AI Чат Помощник",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header_label.pack(pady=(20, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Войдите в систему для продолжения",
            font=ctk.CTkFont(size=14),
            text_color="#6c757d"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Login form
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=20, pady=20)
        
        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="Имя пользователя:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        username_label.pack(anchor="w", pady=(20, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Введите имя пользователя",
            font=ctk.CTkFont(size=12),
            height=40
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="Пароль:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Введите пароль",
            font=ctk.CTkFont(size=12),
            height=40,
            show="*"
        )
        self.password_entry.pack(fill="x", pady=(0, 15))
        
        # Remember me checkbox
        self.remember_me_var = tk.BooleanVar()
        remember_checkbox = ctk.CTkCheckBox(
            form_frame,
            text="Запомнить меня",
            variable=self.remember_me_var,
            font=ctk.CTkFont(size=12)
        )
        remember_checkbox.pack(anchor="w", pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(form_frame)
        buttons_frame.pack(fill="x", pady=(0, 20))
        
        # Login button
        login_btn = ctk.CTkButton(
            buttons_frame,
            text="🔐 Войти",
            command=self.login,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45
        )
        login_btn.pack(fill="x", pady=(0, 10))
        
        # Register button
        register_btn = ctk.CTkButton(
            buttons_frame,
            text="📝 Регистрация",
            command=self.show_register,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="transparent",
            border_width=2,
            border_color="#007bff",
            text_color="#007bff",
            hover_color="#e3f2fd"
        )
        register_btn.pack(fill="x", pady=(0, 10))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Отмена",
            command=self.cancel,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        cancel_btn.pack(fill="x")
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Focus on username field
        self.username_entry.focus()
    
    def center_dialog(self):
        """Center dialog on parent window"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"400x500+{x}+{y}")
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля")
            return
        
        try:
            # Show loading
            self.configure(cursor="wait")
            
            # Attempt login
            result = self.api_client.login(username, password)
            
            if result:
                # Successful login
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            messagebox.showerror("Ошибка", f"Ошибка входа: {str(e)}")
        finally:
            try:
                self.configure(cursor="")
            except:
                pass  # Window might be destroyed
    
    def show_register(self):
        """Show registration form"""
        # Hide login form
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.pack_forget()
        
        # Show registration form
        self.create_register_form()
    
    def create_register_form(self):
        """Create registration form"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="📝 Регистрация",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header_label.pack(pady=(20, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Создайте новый аккаунт",
            font=ctk.CTkFont(size=14),
            text_color="#6c757d"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Registration form
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=20, pady=20)
        
        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="Имя пользователя:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        username_label.pack(anchor="w", pady=(20, 5))
        
        self.reg_username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Введите имя пользователя",
            font=ctk.CTkFont(size=12),
            height=40
        )
        self.reg_username_entry.pack(fill="x", pady=(0, 15))
        
        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="Пароль:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.reg_password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Введите пароль",
            font=ctk.CTkFont(size=12),
            height=40,
            show="*"
        )
        self.reg_password_entry.pack(fill="x", pady=(0, 15))
        
        # Confirm password field
        confirm_password_label = ctk.CTkLabel(
            form_frame,
            text="Подтвердите пароль:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        confirm_password_label.pack(anchor="w", pady=(0, 5))
        
        self.reg_confirm_password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Подтвердите пароль",
            font=ctk.CTkFont(size=12),
            height=40,
            show="*"
        )
        self.reg_confirm_password_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(form_frame)
        buttons_frame.pack(fill="x", pady=(0, 20))
        
        # Register button
        register_btn = ctk.CTkButton(
            buttons_frame,
            text="📝 Зарегистрироваться",
            command=self.register,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45
        )
        register_btn.pack(fill="x", pady=(0, 10))
        
        # Back to login button
        back_btn = ctk.CTkButton(
            buttons_frame,
            text="← Назад к входу",
            command=self.show_login,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="transparent",
            border_width=2,
            border_color="#007bff",
            text_color="#007bff",
            hover_color="#e3f2fd"
        )
        back_btn.pack(fill="x")
        
        # Bind Enter key
        self.reg_confirm_password_entry.bind("<Return>", lambda e: self.register())
    
    def show_login(self):
        """Show login form"""
        # Destroy current widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate login form
        self.create_widgets()
    
    def register(self):
        """Handle registration"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm_password = self.reg_confirm_password_entry.get().strip()
        
        if not username or not password or not confirm_password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля")
            return
        
        if password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        
        if len(password) < 6:
            messagebox.showerror("Ошибка", "Пароль должен содержать минимум 6 символов")
            return
        
        try:
            # Show loading
            self.configure(cursor="wait")
            
            # Attempt registration
            result = self.api_client.register(username, password, username)
            
            if result:
                messagebox.showinfo("Успех", "Регистрация прошла успешно! Теперь вы можете войти.")
                self.show_login()
            else:
                messagebox.showerror("Ошибка", "Регистрация не удалась. Попробуйте еще раз.")
                
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            messagebox.showerror("Ошибка", f"Ошибка регистрации: {str(e)}")
        finally:
            try:
                self.configure(cursor="")
            except:
                pass  # Window might be destroyed
    
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.destroy()
