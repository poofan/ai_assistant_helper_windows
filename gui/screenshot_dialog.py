"""
Screenshot Dialog - Full implementation for modern app
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging
from pathlib import Path
from .coordinates_dialog import CoordinatesDialog

class ScreenshotDialog(ctk.CTkToplevel):
    """Full screenshot settings dialog"""
    
    def __init__(self, parent, screenshot_service, screenshot_settings, coordinates_manager=None):
        super().__init__(parent)
        
        self.screenshot_service = screenshot_service
        self.screenshot_settings = screenshot_settings
        self.coordinates_manager = coordinates_manager
        self.result = False
        self.logger = logging.getLogger(__name__)
        
        self.setup_dialog()
        self.create_widgets()
        self.setup_context_menu()
        self.load_settings()
    
    def setup_dialog(self):
        """Setup dialog properties"""
        self.title("⚙️ Настройки скриншота")
        self.geometry("650x700")
        self.resizable(True, True)
        self.minsize(600, 600)
        
        # Make dialog modal
        self.transient(self.master)
        self.grab_set()
        
        # Center dialog
        self.geometry("+%d+%d" % (self.master.winfo_rootx() + 50, self.master.winfo_rooty() + 50))
    
    def create_widgets(self):
        """Create dialog widgets with adaptive layout"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="⚙️ Настройки скриншота",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=(0, 20))
        
        # Content area with scroll
        content_frame = ctk.CTkScrollableFrame(main_frame, height=450)
        content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Screenshot type selection
        type_frame = ctk.CTkFrame(content_frame)
        type_frame.pack(fill="x", pady=(0, 15))
        
        type_label = ctk.CTkLabel(
            type_frame,
            text="📷 Тип скриншота:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        type_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Screenshot type radio buttons
        self.screenshot_type = tk.StringVar(value="fullscreen")
        
        fullscreen_radio = ctk.CTkRadioButton(
            type_frame,
            text="🖥️ Полный экран",
            variable=self.screenshot_type,
            value="fullscreen",
            font=ctk.CTkFont(size=12)
        )
        fullscreen_radio.pack(anchor="w", padx=30, pady=2)
        
        app_radio = ctk.CTkRadioButton(
            type_frame,
            text="📱 Конкретное приложение",
            variable=self.screenshot_type,
            value="app",
            font=ctk.CTkFont(size=12)
        )
        app_radio.pack(anchor="w", padx=30, pady=2)
        
        # App selection
        app_frame = ctk.CTkFrame(content_frame)
        app_frame.pack(fill="x", pady=(0, 15))
        
        app_label = ctk.CTkLabel(
            app_frame,
            text="📱 Выберите приложение:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        app_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # App listbox
        self.app_listbox = tk.Listbox(
            app_frame,
            height=6,
            font=ctk.CTkFont(size=11),
            bg="#f8f9fa",
            fg="#212529",
            selectbackground="#007bff",
            selectforeground="white",
            border=0,
            highlightthickness=0
        )
        self.app_listbox.pack(fill="x", padx=15, pady=(0, 15))
        
        # Load available apps
        self.load_apps()
        
        # Prompt settings
        prompt_frame = ctk.CTkFrame(content_frame)
        prompt_frame.pack(fill="x", pady=(0, 15))
        
        prompt_label = ctk.CTkLabel(
            prompt_frame,
            text="💬 Промпт для анализа:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        prompt_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Prompt text area
        self.prompt_text = ctk.CTkTextbox(
            prompt_frame,
            height=100,
            font=ctk.CTkFont(size=11)
        )
        self.prompt_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # AI Automation settings
        automation_frame = ctk.CTkFrame(content_frame)
        automation_frame.pack(fill="x", pady=(0, 15))
        
        automation_label = ctk.CTkLabel(
            automation_frame,
            text="🤖 Автоматизация действий:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        automation_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # AI Automation toggle
        self.ai_automation_var = tk.BooleanVar()
        self.ai_automation_checkbox = ctk.CTkCheckBox(
            automation_frame,
            text="Включить автоматическое выполнение действий по ответам ИИ",
            variable=self.ai_automation_var,
            font=ctk.CTkFont(size=12)
        )
        self.ai_automation_checkbox.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Auto Screenshots settings
        auto_screenshots_frame = ctk.CTkFrame(content_frame)
        auto_screenshots_frame.pack(fill="x", pady=(0, 15))
        
        auto_screenshots_label = ctk.CTkLabel(
            auto_screenshots_frame,
            text="📸 Автоматические скриншоты:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        auto_screenshots_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Auto screenshots interval setting
        interval_frame = ctk.CTkFrame(auto_screenshots_frame)
        interval_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        interval_label = ctk.CTkLabel(
            interval_frame,
            text="⏱️ Интервал (секунды):",
            font=ctk.CTkFont(size=12)
        )
        interval_label.pack(side="left", padx=(10, 5), pady=10)
        
        self.auto_screenshots_interval = ctk.CTkEntry(
            interval_frame,
            width=80,
            font=ctk.CTkFont(size=12),
            placeholder_text="5"
        )
        self.auto_screenshots_interval.pack(side="left", padx=(0, 10), pady=10)
        
        # Info label about hotkey
        info_label = ctk.CTkLabel(
            auto_screenshots_frame,
            text="💡 Используйте Ctrl+Shift+S для включения/выключения автоматических скриншотов",
            font=ctk.CTkFont(size=11),
            text_color="#6c757d"
        )
        info_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Fixed buttons frame at bottom
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Coordinates button (if coordinates_manager is available)
        if self.coordinates_manager:
            coordinates_btn = ctk.CTkButton(
                buttons_frame,
                text="🎯 Координаты",
                command=self.show_coordinates_dialog,
                font=ctk.CTkFont(size=12),
                height=40,
                fg_color="#17a2b8",
                hover_color="#138496"
            )
            coordinates_btn.pack(side="left", padx=(10, 5), pady=10)
        
        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Сохранить",
            command=self.save_settings,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        save_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Отмена",
            command=self.cancel_clicked,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        cancel_btn.pack(side="right", padx=(10, 5), pady=10)
    
    def load_apps(self):
        """Load available applications"""
        try:
            import psutil
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe'] and proc.info['name']:
                        app_name = proc.info['name']
                        app_path = proc.info['exe']
                        apps.append(f"{app_name} ({app_path})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Remove duplicates and sort
            apps = sorted(list(set(apps)))
            
            for app in apps:
                self.app_listbox.insert(tk.END, app)
                
        except Exception as e:
            self.logger.error(f"Error loading apps: {e}")
            self.app_listbox.insert(tk.END, "Ошибка загрузки приложений")
    
    def load_settings(self):
        """Load current settings"""
        try:
            settings = self.screenshot_settings.get_settings()
            
            # Load screenshot type
            screenshot_type = settings.get("screenshot_type", "fullscreen")
            self.screenshot_type.set(screenshot_type)
            
            # Load prompt
            prompt = settings.get("prompt", "Проанализируй этот скриншот максимально подробно на русском языке.")
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", prompt)
            
            # Load AI automation setting
            ai_automation_enabled = settings.get("ai_automation_enabled", False)
            self.ai_automation_var.set(ai_automation_enabled)
            
            # Load auto screenshots interval
            auto_screenshots_interval = settings.get("auto_screenshots_interval", 5)
            self.auto_screenshots_interval.delete(0, tk.END)
            self.auto_screenshots_interval.insert(0, str(auto_screenshots_interval))
            
            # Load selected app
            selected_app = settings.get("selected_app")
            if selected_app:
                for i in range(self.app_listbox.size()):
                    if selected_app in self.app_listbox.get(i):
                        self.app_listbox.selection_set(i)
                        break
                        
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings"""
        try:
            # Get screenshot type
            screenshot_type = self.screenshot_type.get()
            
            # Get prompt
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            
            # Get selected app
            selected_app = None
            selection = self.app_listbox.curselection()
            if selection:
                selected_app = self.app_listbox.get(selection[0])
            
            # Get AI automation setting
            ai_automation_enabled = self.ai_automation_var.get()
            
            # Get auto screenshots interval
            try:
                auto_screenshots_interval = int(self.auto_screenshots_interval.get() or "5")
                if auto_screenshots_interval < 1:
                    auto_screenshots_interval = 5
            except ValueError:
                auto_screenshots_interval = 5
            
            # Update settings
            self.screenshot_settings.update_settings(
                screenshot_type=screenshot_type,
                prompt=prompt,
                selected_app=selected_app,
                ai_automation_enabled=ai_automation_enabled,
                auto_screenshots_interval=auto_screenshots_interval
            )
            
            self.result = True
            messagebox.showinfo("Успех", "Настройки скриншота сохранены!")
            self.destroy()
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Ошибка", f"Ошибка сохранения настроек: {str(e)}")
    
    def cancel_clicked(self):
        """Cancel button clicked"""
        self.result = False
        self.destroy()
    
    def show_coordinates_dialog(self):
        """Show coordinates settings dialog"""
        try:
            if self.coordinates_manager:
                self.logger.info("Opening coordinates dialog from screenshot settings")
                coordinates_dialog = CoordinatesDialog(self, self.coordinates_manager)
                if coordinates_dialog.result:
                    self.logger.info("Coordinates updated successfully")
            else:
                messagebox.showwarning("Предупреждение", "Менеджер координат не доступен")
        except Exception as e:
            self.logger.error(f"Error showing coordinates dialog: {e}")
            messagebox.showerror("Ошибка", f"Ошибка открытия диалога координат: {e}")
    
    def setup_context_menu(self):
        """Setup context menu for copy/paste functionality"""
        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выделить все", command=self.select_all)
        
        # Bind context menu and keyboard shortcuts to prompt text
        self.prompt_text.bind("<Button-3>", self.show_context_menu)
        self.prompt_text.bind("<Control-c>", lambda e: self.copy_text())
        self.prompt_text.bind("<Control-v>", lambda e: self.paste_text())
        self.prompt_text.bind("<Control-a>", lambda e: self.select_all())
    
    def show_context_menu(self, event):
        """Show context menu at cursor position"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_text(self):
        """Copy selected text to clipboard"""
        try:
            # Get selected text from prompt text
            if self.prompt_text.selection_get():
                selected_text = self.prompt_text.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.logger.info("Text copied to clipboard")
        except tk.TclError:
            # No text selected
            pass
    
    def paste_text(self):
        """Paste text from clipboard to prompt text"""
        try:
            clipboard_text = self.clipboard_get()
            if clipboard_text:
                # Insert at cursor position in prompt text
                cursor_pos = self.prompt_text.index(tk.INSERT)
                self.prompt_text.insert(cursor_pos, clipboard_text)
                self.logger.info("Text pasted from clipboard")
        except tk.TclError:
            # No text in clipboard
            pass
    
    def select_all(self):
        """Select all text in the prompt text"""
        try:
            self.prompt_text.tag_add(tk.SEL, "1.0", tk.END)
            self.prompt_text.mark_set(tk.INSERT, "1.0")
            self.prompt_text.see(tk.INSERT)
        except Exception as e:
            self.logger.error(f"Error selecting text: {e}")
