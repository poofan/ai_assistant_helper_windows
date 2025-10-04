"""
Coordinates Settings Dialog for managing UI element coordinates
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging
from typing import Dict, List, Optional

class CoordinatesDialog(ctk.CTkToplevel):
    """Dialog for managing UI element coordinates"""
    
    def __init__(self, parent, coordinates_manager):
        super().__init__(parent)
        
        self.coordinates_manager = coordinates_manager
        self.result = False
        self.logger = logging.getLogger(__name__)
        
        self.setup_dialog()
        self.create_widgets()
        self.setup_context_menu()
        self.load_coordinates()
    
    def setup_dialog(self):
        """Setup dialog properties"""
        self.title("🎯 Настройки координат элементов")
        self.geometry("800x600")
        self.resizable(True, True)
        self.minsize(800, 600)
        
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
        
        # Instructions
        instructions_label = ctk.CTkLabel(
            main_frame,
            text="Настройте координаты элементов интерфейса для автоматизации.\nФормат: [X, Y, Ширина, Высота]",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        instructions_label.pack(pady=(0, 20))
        
        # Coordinates frame
        coords_frame = ctk.CTkFrame(main_frame)
        coords_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create scrollable frame for coordinates
        self.scroll_frame = ctk.CTkScrollableFrame(
            coords_frame,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Store coordinate entry widgets
        self.coord_entries = {}
        
        # Create coordinate entries
        self.create_coordinate_entries()
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Reset button
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Сбросить",
            command=self.reset_coordinates,
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color="#ffc107",
            hover_color="#e0a800"
        )
        reset_btn.pack(side="left", padx=(10, 5), pady=10)
        
        # Test button
        test_btn = ctk.CTkButton(
            buttons_frame,
            text="🧪 Тест",
            command=self.test_coordinates,
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color="#17a2b8",
            hover_color="#138496"
        )
        test_btn.pack(side="left", padx=5, pady=10)
        
        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Сохранить",
            command=self.save_coordinates,
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
    
    def create_coordinate_entries(self):
        """Create coordinate entry widgets"""
        # Element descriptions
        element_descriptions = {
            "player_cards": "Карты игрока",
            "player_balance": "Баланс игрока",
            "table_cards": "Карты на столе",
            "bank_total": "Общий банк",
            "button_fold": "Кнопка 'Скинуть'",
            "button_call": "Кнопка 'Уравнять'",
            "button_raise": "Кнопка 'Повысить'",
            "button_check": "Кнопка 'Пропустить'"
        }
        
        for element_name, description in element_descriptions.items():
            # Element frame
            element_frame = ctk.CTkFrame(self.scroll_frame)
            element_frame.pack(fill="x", pady=5)
            
            # Element name and description
            name_label = ctk.CTkLabel(
                element_frame,
                text=f"{description} ({element_name})",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            name_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            # Coordinates frame
            coords_frame = ctk.CTkFrame(element_frame)
            coords_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            # Coordinate labels and entries
            coord_labels = ["X:", "Y:", "Ширина:", "Высота:"]
            coord_keys = ["x", "y", "width", "height"]
            
            coord_entries = {}
            for i, (label, key) in enumerate(zip(coord_labels, coord_keys)):
                # Label
                coord_label = ctk.CTkLabel(
                    coords_frame,
                    text=label,
                    font=ctk.CTkFont(size=12),
                    width=60
                )
                coord_label.grid(row=0, column=i*2, padx=(10, 5), pady=10)
                
                # Entry
                coord_entry = ctk.CTkEntry(
                    coords_frame,
                    width=80,
                    font=ctk.CTkFont(size=12)
                )
                coord_entry.grid(row=0, column=i*2+1, padx=(0, 10), pady=10)
                coord_entries[key] = coord_entry
            
            self.coord_entries[element_name] = coord_entries
    
    def load_coordinates(self):
        """Load coordinates into entry widgets"""
        try:
            coordinates = self.coordinates_manager.get_all_coordinates()
            
            for element_name, coords in coordinates.items():
                if element_name in self.coord_entries:
                    entries = self.coord_entries[element_name]
                    if len(coords) == 4:
                        entries["x"].delete(0, tk.END)
                        entries["x"].insert(0, str(coords[0]))
                        entries["y"].delete(0, tk.END)
                        entries["y"].insert(0, str(coords[1]))
                        entries["width"].delete(0, tk.END)
                        entries["width"].insert(0, str(coords[2]))
                        entries["height"].delete(0, tk.END)
                        entries["height"].insert(0, str(coords[3]))
            
            self.logger.info("Loaded coordinates into dialog")
        except Exception as e:
            self.logger.error(f"Error loading coordinates: {e}")
            messagebox.showerror("Ошибка", f"Ошибка загрузки координат: {e}")
    
    def save_coordinates(self):
        """Save coordinates from entry widgets"""
        try:
            updates = {}
            
            for element_name, entries in self.coord_entries.items():
                try:
                    x = int(entries["x"].get())
                    y = int(entries["y"].get())
                    width = int(entries["width"].get())
                    height = int(entries["height"].get())
                    
                    if x < 0 or y < 0 or width <= 0 or height <= 0:
                        raise ValueError(f"Неверные координаты для {element_name}")
                    
                    updates[element_name] = [x, y, width, height]
                except ValueError as e:
                    messagebox.showerror("Ошибка", f"Неверные координаты для {element_name}: {e}")
                    return
            
            if self.coordinates_manager.update_coordinates(updates):
                if self.coordinates_manager.save_coordinates():
                    messagebox.showinfo("Успех", "Координаты сохранены успешно!")
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить координаты")
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить координаты")
                
        except Exception as e:
            self.logger.error(f"Error saving coordinates: {e}")
            messagebox.showerror("Ошибка", f"Ошибка сохранения координат: {e}")
    
    def reset_coordinates(self):
        """Reset coordinates to default values"""
        try:
            if messagebox.askyesno("Подтверждение", "Сбросить все координаты к значениям по умолчанию?"):
                self.coordinates_manager.reset_to_defaults()
                self.load_coordinates()
                messagebox.showinfo("Успех", "Координаты сброшены к значениям по умолчанию")
        except Exception as e:
            self.logger.error(f"Error resetting coordinates: {e}")
            messagebox.showerror("Ошибка", f"Ошибка сброса координат: {e}")
    
    def test_coordinates(self):
        """Test coordinates by showing element info"""
        try:
            test_info = []
            for element_name, entries in self.coord_entries.items():
                try:
                    x = int(entries["x"].get())
                    y = int(entries["y"].get())
                    width = int(entries["width"].get())
                    height = int(entries["height"].get())
                    
                    center_x = x + width // 2
                    center_y = y + height // 2
                    
                    test_info.append(f"{element_name}: [{x}, {y}, {width}, {height}] -> Центр: ({center_x}, {center_y})")
                except ValueError:
                    test_info.append(f"{element_name}: Неверные координаты")
            
            messagebox.showinfo("Тест координат", "\n".join(test_info))
        except Exception as e:
            self.logger.error(f"Error testing coordinates: {e}")
            messagebox.showerror("Ошибка", f"Ошибка тестирования координат: {e}")
    
    def cancel_clicked(self):
        """Handle cancel button click"""
        self.result = False
        self.destroy()
    
    def setup_context_menu(self):
        """Setup context menu for copy/paste functionality"""
        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Выделить все", command=self.select_all)
        
        # Bind context menu and keyboard shortcuts to all entry widgets
        for element_name, entries in self.coord_entries.items():
            for key, entry in entries.items():
                # Bind right-click to show context menu
                entry.bind("<Button-3>", self.show_context_menu)
                
                # Bind keyboard shortcuts
                entry.bind("<Control-c>", lambda e: self.copy_text())
                entry.bind("<Control-v>", lambda e: self.paste_text())
                entry.bind("<Control-a>", lambda e: self.select_all())
    
    def show_context_menu(self, event):
        """Show context menu at cursor position"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_text(self):
        """Copy selected text to clipboard"""
        try:
            # Get the focused widget
            focused = self.focus_get()
            if hasattr(focused, 'selection_get'):
                selected_text = focused.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.logger.info("Text copied to clipboard")
        except tk.TclError:
            # No text selected
            pass
    
    def paste_text(self):
        """Paste text from clipboard to focused widget"""
        try:
            clipboard_text = self.clipboard_get()
            if clipboard_text:
                # Get the focused widget
                focused = self.focus_get()
                if hasattr(focused, 'insert'):
                    # Insert at cursor position
                    cursor_pos = focused.index(tk.INSERT)
                    current_text = focused.get()
                    new_text = current_text[:cursor_pos] + clipboard_text + current_text[cursor_pos:]
                    focused.delete(0, tk.END)
                    focused.insert(0, new_text)
                    self.logger.info("Text pasted from clipboard")
        except tk.TclError:
            # No text in clipboard
            pass
    
    def select_all(self):
        """Select all text in the focused widget"""
        try:
            focused = self.focus_get()
            if hasattr(focused, 'select_range'):
                focused.select_range(0, tk.END)
        except Exception as e:
            self.logger.error(f"Error selecting text: {e}")
