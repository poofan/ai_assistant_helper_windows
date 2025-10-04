"""
Flexible Coordinates Settings Dialog for managing UI element coordinates
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging
from typing import Dict, List, Optional

class CoordinatesDialog(ctk.CTkToplevel):
    """Dialog for managing UI element coordinates with flexible button system"""
    
    def __init__(self, parent, coordinates_manager):
        super().__init__(parent)
        
        self.coordinates_manager = coordinates_manager
        self.result = False
        self.logger = logging.getLogger(__name__)
        
        # Current editing state
        self.current_button_id = None
        self.button_entries = {}
        
        self.setup_dialog()
        self.create_widgets()
        self.setup_context_menu()
        self.load_coordinates()
    
    def setup_dialog(self):
        """Setup dialog properties"""
        self.title("🎯 Настройки координат элементов")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.minsize(800, 600)  # Более гибкий минимальный размер
        
        # Make dialog modal
        self.transient(self.master)
        self.grab_set()
        
        # Center dialog
        self.geometry("+%d+%d" % (self.master.winfo_rootx() + 50, self.master.winfo_rooty() + 50))
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="🎯 Настройки координат элементов",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Buttons tab
        self.buttons_tab = self.notebook.add("🎮 Кнопки")
        self.create_buttons_tab()
        
        # Info elements tab
        self.info_tab = self.notebook.add("ℹ️ Информация")
        self.create_info_tab()
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Сохранить",
            command=self.save_coordinates,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=120
        )
        save_btn.pack(side="right", padx=(10, 0))
        
        # Reset button
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Сброс",
            command=self.reset_coordinates,
            font=ctk.CTkFont(size=14),
            height=40,
            width=120,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        reset_btn.pack(side="right", padx=10)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Отмена",
            command=self.cancel_dialog,
            font=ctk.CTkFont(size=14),
            height=40,
            width=120,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        cancel_btn.pack(side="right")
    
    def create_buttons_tab(self):
        """Create buttons management tab"""
        # Header frame
        header_frame = ctk.CTkFrame(self.buttons_tab)
        header_frame.pack(fill="x", pady=(0, 10))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="🎮 Управление кнопками",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(side="left", padx=15, pady=15)
        
        # Add button
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Добавить кнопку",
            command=self.add_new_button,
            font=ctk.CTkFont(size=12),
            height=35,
            width=150
        )
        add_btn.pack(side="right", padx=15, pady=15)
        
        # Buttons list frame
        list_frame = ctk.CTkFrame(self.buttons_tab)
        list_frame.pack(fill="both", expand=True)
        
        # Scrollable frame for buttons
        self.buttons_scroll_frame = ctk.CTkScrollableFrame(list_frame, height=400)
        self.buttons_scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    def create_info_tab(self):
        """Create info elements tab"""
        # Header
        header_label = ctk.CTkLabel(
            self.info_tab,
            text="ℹ️ Информационные элементы (только для просмотра)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(pady=(0, 15))
        
        # Info elements list
        info_frame = ctk.CTkFrame(self.info_tab)
        info_frame.pack(fill="both", expand=True)
        
        self.info_scroll_frame = ctk.CTkScrollableFrame(info_frame, height=400)
        self.info_scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
    def add_new_button(self):
        """Add a new button"""
        dialog = NewButtonDialog(self, self.coordinates_manager)
        self.wait_window(dialog)
        
        if dialog.result:
            self.load_coordinates()
    
    def create_button_widget(self, button_id: str, button_data: Dict):
        """Create widget for a button with responsive layout"""
        button_frame = ctk.CTkFrame(self.buttons_scroll_frame)
        button_frame.pack(fill="x", pady=5)
        
        # Top row - ID and Name
        top_frame = ctk.CTkFrame(button_frame)
        top_frame.pack(fill="x", padx=5, pady=5)
        
        # Button ID (read-only)
        id_label = ctk.CTkLabel(
            top_frame,
            text=f"ID: {button_id}",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120
        )
        id_label.pack(side="left", padx=5, pady=5)
        
        # Name entry
        name_label = ctk.CTkLabel(top_frame, text="Название:", width=70)
        name_label.pack(side="left", padx=5, pady=5)
        
        name_entry = ctk.CTkEntry(
            top_frame,
            placeholder_text="Название кнопки",
            width=180
        )
        name_entry.insert(0, button_data.get("name", ""))
        name_entry.pack(side="left", padx=5, pady=5)
        
        # Middle row - Coordinates
        coords_frame = ctk.CTkFrame(button_frame)
        coords_frame.pack(fill="x", padx=5, pady=2)
        
        coords_label = ctk.CTkLabel(coords_frame, text="Координаты:", width=70)
        coords_label.pack(side="left", padx=5, pady=5)
        
        coords = button_data.get("coordinates", [0, 0, 100, 50])
        
        # X coordinate
        x_label = ctk.CTkLabel(coords_frame, text="X:", width=20)
        x_label.pack(side="left", padx=2, pady=5)
        x_entry = ctk.CTkEntry(coords_frame, placeholder_text="X", width=60)
        x_entry.insert(0, str(coords[0]) if len(coords) > 0 else "0")
        x_entry.pack(side="left", padx=2, pady=5)
        
        # Y coordinate
        y_label = ctk.CTkLabel(coords_frame, text="Y:", width=20)
        y_label.pack(side="left", padx=2, pady=5)
        y_entry = ctk.CTkEntry(coords_frame, placeholder_text="Y", width=60)
        y_entry.insert(0, str(coords[1]) if len(coords) > 1 else "0")
        y_entry.pack(side="left", padx=2, pady=5)
        
        # W coordinate
        w_label = ctk.CTkLabel(coords_frame, text="W:", width=20)
        w_label.pack(side="left", padx=2, pady=5)
        w_entry = ctk.CTkEntry(coords_frame, placeholder_text="W", width=60)
        w_entry.insert(0, str(coords[2]) if len(coords) > 2 else "100")
        w_entry.pack(side="left", padx=2, pady=5)
        
        # H coordinate
        h_label = ctk.CTkLabel(coords_frame, text="H:", width=20)
        h_label.pack(side="left", padx=2, pady=5)
        h_entry = ctk.CTkEntry(coords_frame, placeholder_text="H", width=60)
        h_entry.insert(0, str(coords[3]) if len(coords) > 3 else "50")
        h_entry.pack(side="left", padx=2, pady=5)
        
        # Bottom row - Description and Action buttons
        bottom_frame = ctk.CTkFrame(button_frame)
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Description entry
        desc_label = ctk.CTkLabel(bottom_frame, text="Описание:", width=70)
        desc_label.pack(side="left", padx=5, pady=5)
        
        desc_entry = ctk.CTkEntry(
            bottom_frame,
            placeholder_text="Описание кнопки",
            width=250
        )
        desc_entry.insert(0, button_data.get("description", ""))
        desc_entry.pack(side="left", padx=5, pady=5)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(bottom_frame)
        actions_frame.pack(side="right", padx=5, pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            actions_frame,
            text="💾 Сохр.",
            command=lambda: self.save_button(button_id, name_entry, [x_entry, y_entry, w_entry, h_entry], desc_entry),
            width=70,
            height=30,
            font=ctk.CTkFont(size=10)
        )
        save_btn.pack(side="left", padx=2)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Уд.",
            command=lambda: self.delete_button(button_id),
            width=60,
            height=30,
            fg_color="#dc3545",
            hover_color="#c82333",
            font=ctk.CTkFont(size=10)
        )
        delete_btn.pack(side="left", padx=2)
        
        # Test button
        test_btn = ctk.CTkButton(
            actions_frame,
            text="🎯 Тест",
            command=lambda: self.test_button(button_id),
            width=70,
            height=30,
            fg_color="#28a745",
            hover_color="#218838",
            font=ctk.CTkFont(size=10)
        )
        test_btn.pack(side="left", padx=2)
    
    def create_info_element_widget(self, element_id: str, element_data: Dict):
        """Create widget for an info element with responsive layout"""
        element_frame = ctk.CTkFrame(self.info_scroll_frame)
        element_frame.pack(fill="x", pady=5)
        
        # Top row - ID and Name
        top_frame = ctk.CTkFrame(element_frame)
        top_frame.pack(fill="x", padx=5, pady=5)
        
        # Element ID
        id_label = ctk.CTkLabel(
            top_frame,
            text=f"ID: {element_id}",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120
        )
        id_label.pack(side="left", padx=5, pady=5)
        
        # Name
        name_label = ctk.CTkLabel(
            top_frame,
            text=f"Название: {element_data.get('name', '')}",
            width=200
        )
        name_label.pack(side="left", padx=5, pady=5)
        
        # Bottom row - Coordinates and Description
        bottom_frame = ctk.CTkFrame(element_frame)
        bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Coordinates
        coords = element_data.get("coordinates", [])
        coords_text = f"Координаты: X:{coords[0]}, Y:{coords[1]}, W:{coords[2]}, H:{coords[3]}" if len(coords) >= 4 else "Нет координат"
        coords_label = ctk.CTkLabel(
            bottom_frame,
            text=coords_text,
            width=300
        )
        coords_label.pack(side="left", padx=5, pady=5)
        
        # Description
        desc_text = element_data.get("description", "")
        if desc_text:
            desc_label = ctk.CTkLabel(
                bottom_frame,
                text=f"Описание: {desc_text}",
                width=400
            )
            desc_label.pack(side="left", padx=5, pady=5)
    
    def save_button(self, button_id: str, name_entry, coord_entries, desc_entry):
        """Save button changes"""
        try:
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Название кнопки не может быть пустым")
                return
            
            coords = []
            for entry in coord_entries:
                try:
                    coords.append(int(entry.get() or "0"))
                except ValueError:
                    messagebox.showerror("Ошибка", "Координаты должны быть целыми числами")
                    return
            
            if len(coords) != 4:
                messagebox.showerror("Ошибка", "Необходимо указать все 4 координаты (X, Y, W, H)")
                return
            
            if not self.coordinates_manager.validate_coordinates(coords):
                messagebox.showerror("Ошибка", "Некорректные координаты")
                return
            
            description = desc_entry.get().strip()
            
            success = self.coordinates_manager.update_button(
                button_id, name, coords, description
            )
            
            if success:
                messagebox.showinfo("Успех", f"Кнопка '{name}' сохранена")
                self.load_coordinates()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить кнопку")
                
        except Exception as e:
            self.logger.error(f"Error saving button {button_id}: {e}")
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def delete_button(self, button_id: str):
        """Delete a button"""
        try:
            button_info = self.coordinates_manager.get_button_info(button_id)
            button_name = button_info.get("name", button_id) if button_info else button_id
            
            if messagebox.askyesno("Подтверждение", f"Удалить кнопку '{button_name}' ({button_id})?"):
                success = self.coordinates_manager.remove_button(button_id)
                if success:
                    messagebox.showinfo("Успех", "Кнопка удалена")
                    self.load_coordinates()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить кнопку")
        except Exception as e:
            self.logger.error(f"Error deleting button {button_id}: {e}")
            messagebox.showerror("Ошибка", f"Ошибка удаления: {str(e)}")
    
    def test_button(self, button_id: str):
        """Test button click"""
        try:
            from services.automation_service import AutomationService
            automation = AutomationService(self.coordinates_manager)
            
            success = automation.perform_button_action(button_id)
            if success:
                messagebox.showinfo("Тест", "Кнопка нажата успешно!")
            else:
                messagebox.showerror("Тест", "Не удалось нажать кнопку")
        except Exception as e:
            self.logger.error(f"Error testing button {button_id}: {e}")
            messagebox.showerror("Ошибка", f"Ошибка тестирования: {str(e)}")
    
    def load_coordinates(self):
        """Load coordinates into dialog"""
        try:
            # Clear existing widgets
            for widget in self.buttons_scroll_frame.winfo_children():
                widget.destroy()
            
            for widget in self.info_scroll_frame.winfo_children():
                widget.destroy()
            
            # Load buttons
            buttons = self.coordinates_manager.get_all_buttons()
            if buttons:
                for button_id, button_data in buttons.items():
                    self.create_button_widget(button_id, button_data)
            else:
                no_buttons_label = ctk.CTkLabel(
                    self.buttons_scroll_frame,
                    text="Нет кнопок. Нажмите 'Добавить кнопку' для создания.",
                    font=ctk.CTkFont(size=14),
                    text_color="#6c757d"
                )
                no_buttons_label.pack(pady=50)
            
            # Load info elements
            info_elements = self.coordinates_manager.get_all_info_elements()
            if info_elements:
                for element_id, element_data in info_elements.items():
                    self.create_info_element_widget(element_id, element_data)
            else:
                no_info_label = ctk.CTkLabel(
                    self.info_scroll_frame,
                    text="Нет информационных элементов",
                    font=ctk.CTkFont(size=14),
                    text_color="#6c757d"
                )
                no_info_label.pack(pady=50)
            
            self.logger.info("Loaded coordinates into dialog")
            
        except Exception as e:
            self.logger.error(f"Error loading coordinates: {e}")
            messagebox.showerror("Ошибка", f"Ошибка загрузки координат: {str(e)}")
    
    def save_coordinates(self):
        """Save all coordinates"""
        try:
            success = self.coordinates_manager.save_coordinates()
            if success:
                messagebox.showinfo("Успех", "Координаты сохранены")
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить координаты")
        except Exception as e:
            self.logger.error(f"Error saving coordinates: {e}")
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def reset_coordinates(self):
        """Reset coordinates to defaults"""
        if messagebox.askyesno("Подтверждение", "Сбросить все координаты к значениям по умолчанию?"):
            try:
                success = self.coordinates_manager.reset_to_defaults()
                if success:
                    messagebox.showinfo("Успех", "Координаты сброшены")
                    self.load_coordinates()
                else:
                    messagebox.showerror("Ошибка", "Не удалось сбросить координаты")
            except Exception as e:
                self.logger.error(f"Error resetting coordinates: {e}")
                messagebox.showerror("Ошибка", f"Ошибка сброса: {str(e)}")
    
    def cancel_dialog(self):
        """Cancel dialog"""
        self.destroy()
    
    def setup_context_menu(self):
        """Setup context menu for copy/paste"""
        pass  # Can be implemented later if needed


class NewButtonDialog(ctk.CTkToplevel):
    """Dialog for creating new button"""
    
    def __init__(self, parent, coordinates_manager):
        super().__init__(parent)
        
        self.coordinates_manager = coordinates_manager
        self.result = False
        self.logger = logging.getLogger(__name__)
        
        self.setup_dialog()
        self.create_widgets()
    
    def setup_dialog(self):
        """Setup dialog properties"""
        self.title("➕ Добавить новую кнопку")
        self.geometry("500x400")
        self.resizable(True, True)
        self.minsize(450, 350)
        
        # Make dialog modal
        self.transient(self.master)
        self.grab_set()
        
        # Center dialog
        self.geometry("+%d+%d" % (self.master.winfo_rootx() + 100, self.master.winfo_rooty() + 100))
    
    def create_widgets(self):
        """Create dialog widgets with adaptive layout"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="➕ Добавить новую кнопку",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack(pady=(0, 20))
        
        # Content area with scroll
        content_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        content_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Button ID
        id_label = ctk.CTkLabel(content_frame, text="ID кнопки:")
        id_label.pack(anchor="w", pady=(0, 5))
        
        self.id_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Например: my_button",
            height=35
        )
        self.id_entry.pack(fill="x", pady=(0, 15))
        
        # Button name
        name_label = ctk.CTkLabel(content_frame, text="Название:")
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Например: Моя кнопка",
            height=35
        )
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # Coordinates
        coords_label = ctk.CTkLabel(content_frame, text="Координаты (X, Y, W, H):")
        coords_label.pack(anchor="w", pady=(0, 5))
        
        coords_frame = ctk.CTkFrame(content_frame)
        coords_frame.pack(fill="x", pady=(0, 15))
        
        # X coordinate
        x_row = ctk.CTkFrame(coords_frame)
        x_row.pack(fill="x", padx=10, pady=2)
        x_label = ctk.CTkLabel(x_row, text="X:", width=30)
        x_label.pack(side="left", padx=(0, 5))
        self.x_entry = ctk.CTkEntry(x_row, placeholder_text="X", width=100, height=30)
        self.x_entry.pack(side="left", padx=(0, 10))
        self.x_entry.insert(0, "100")
        
        # Y coordinate
        y_row = ctk.CTkFrame(coords_frame)
        y_row.pack(fill="x", padx=10, pady=2)
        y_label = ctk.CTkLabel(y_row, text="Y:", width=30)
        y_label.pack(side="left", padx=(0, 5))
        self.y_entry = ctk.CTkEntry(y_row, placeholder_text="Y", width=100, height=30)
        self.y_entry.pack(side="left", padx=(0, 10))
        self.y_entry.insert(0, "100")
        
        # W coordinate
        w_row = ctk.CTkFrame(coords_frame)
        w_row.pack(fill="x", padx=10, pady=2)
        w_label = ctk.CTkLabel(w_row, text="W:", width=30)
        w_label.pack(side="left", padx=(0, 5))
        self.w_entry = ctk.CTkEntry(w_row, placeholder_text="W", width=100, height=30)
        self.w_entry.pack(side="left", padx=(0, 10))
        self.w_entry.insert(0, "100")
        
        # H coordinate
        h_row = ctk.CTkFrame(coords_frame)
        h_row.pack(fill="x", padx=10, pady=2)
        h_label = ctk.CTkLabel(h_row, text="H:", width=30)
        h_label.pack(side="left", padx=(0, 5))
        self.h_entry = ctk.CTkEntry(h_row, placeholder_text="H", width=100, height=30)
        self.h_entry.pack(side="left", padx=(0, 10))
        self.h_entry.insert(0, "50")
        
        # Description
        desc_label = ctk.CTkLabel(content_frame, text="Описание:")
        desc_label.pack(anchor="w", pady=(0, 5))
        
        self.desc_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Описание кнопки",
            height=35
        )
        self.desc_entry.pack(fill="x", pady=(0, 15))
        
        # Fixed buttons frame at bottom
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Отмена",
            command=self.cancel_dialog,
            font=ctk.CTkFont(size=14),
            height=40,
            width=120,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        # Create button
        create_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Создать",
            command=self.create_button,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=120
        )
        create_btn.pack(side="right")
    
    def create_button(self):
        """Create new button"""
        try:
            button_id = self.id_entry.get().strip()
            if not button_id:
                messagebox.showerror("Ошибка", "ID кнопки не может быть пустым")
                return
            
            # Check if button ID already exists
            if self.coordinates_manager.get_button_coordinates(button_id):
                messagebox.showerror("Ошибка", f"Кнопка с ID '{button_id}' уже существует")
                return
            
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Название кнопки не может быть пустым")
                return
            
            coords = []
            for entry in [self.x_entry, self.y_entry, self.w_entry, self.h_entry]:
                try:
                    coords.append(int(entry.get() or "0"))
                except ValueError:
                    messagebox.showerror("Ошибка", "Координаты должны быть целыми числами")
                    return
            
            if not self.coordinates_manager.validate_coordinates(coords):
                messagebox.showerror("Ошибка", "Некорректные координаты")
                return
            
            description = self.desc_entry.get().strip()
            
            success = self.coordinates_manager.add_button(button_id, name, coords, description)
            
            if success:
                messagebox.showinfo("Успех", f"Кнопка '{name}' создана")
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать кнопку")
                
        except Exception as e:
            self.logger.error(f"Error creating button: {e}")
            messagebox.showerror("Ошибка", f"Ошибка создания: {str(e)}")
    
    def cancel_dialog(self):
        """Cancel dialog"""
        self.destroy()
