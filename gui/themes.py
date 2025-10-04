#!/usr/bin/env python3
"""
Темы оформления для AI Chat Messenger
"""

class Theme:
    """Базовый класс для темы"""
    
    def __init__(self, name, colors, fonts):
        self.name = name
        self.colors = colors
        self.fonts = fonts

class LightTheme(Theme):
    """Светлая тема"""
    
    def __init__(self):
        colors = {
            # Основные цвета
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            
            # Фон
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8f9fa',
            'bg_tertiary': '#e9ecef',
            
            # Текст
            'text_primary': '#212529',
            'text_secondary': '#6c757d',
            'text_muted': '#868e96',
            
            # Границы
            'border_light': '#dee2e6',
            'border_medium': '#ced4da',
            'border_dark': '#adb5bd',
            
            # Чат
            'chat_bg': '#f8f9fa',
            'message_user_bg': '#007bff',
            'message_user_text': '#ffffff',
            'message_ai_bg': '#ffffff',
            'message_ai_text': '#212529',
            'message_error_bg': '#ffebee',
            'message_error_text': '#c62828',
            
            # Markdown элементы
            'header_color': '#495057',
            'bullet_color': '#6c757d',
            'number_color': '#6c757d',
            'code_bg': '#f8f9fa',
            'code_text': '#e83e8c',
            
            # Боковая панель
            'sidebar_bg': '#f8f9fa',
            'sidebar_text': '#495057',
            'sidebar_hover': '#e9ecef',
            'sidebar_active': '#007bff',
            'sidebar_active_text': '#ffffff',
            
            # Кнопки
            'btn_primary_bg': '#007bff',
            'btn_primary_text': '#ffffff',
            'btn_primary_hover': '#0056b3',
            'btn_secondary_bg': '#6c757d',
            'btn_secondary_text': '#ffffff',
            'btn_secondary_hover': '#545b62',
            
            # Поля ввода
            'input_bg': '#ffffff',
            'input_border': '#ced4da',
            'input_focus': '#007bff',
            'input_text': '#495057',
            
            # Скроллбары
            'scrollbar_bg': '#f1f3f4',
            'scrollbar_thumb': '#c1c8cd',
            'scrollbar_thumb_hover': '#a8b2ba'
        }
        
        fonts = {
            'primary': ('Segoe UI', 9),
            'secondary': ('Segoe UI', 8),
            'heading': ('Segoe UI', 12, 'bold'),
            'message': ('Segoe UI', 11),
            'timestamp': ('Segoe UI', 8),
            'button': ('Segoe UI', 9)
        }
        
        super().__init__('Light', colors, fonts)

class DarkTheme(Theme):
    """Темная тема"""
    
    def __init__(self):
        colors = {
            # Основные цвета
            'primary': '#0d6efd',
            'secondary': '#6c757d',
            'success': '#198754',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#0dcaf0',
            
            # Фон
            'bg_primary': '#212529',
            'bg_secondary': '#343a40',
            'bg_tertiary': '#495057',
            
            # Текст
            'text_primary': '#ffffff',
            'text_secondary': '#adb5bd',
            'text_muted': '#6c757d',
            
            # Границы
            'border_light': '#495057',
            'border_medium': '#6c757d',
            'border_dark': '#adb5bd',
            
            # Чат
            'chat_bg': '#1a1a1a',
            'message_user_bg': '#0d6efd',
            'message_user_text': '#ffffff',
            'message_ai_bg': '#2d3748',
            'message_ai_text': '#ffffff',
            'message_error_bg': '#4a1a1a',
            'message_error_text': '#ffcdd2',
            
            # Markdown элементы
            'header_color': '#ffffff',
            'bullet_color': '#adb5bd',
            'number_color': '#adb5bd',
            'code_bg': '#495057',
            'code_text': '#ffc107',
            
            # Боковая панель
            'sidebar_bg': '#343a40',
            'sidebar_text': '#adb5bd',
            'sidebar_hover': '#495057',
            'sidebar_active': '#0d6efd',
            'sidebar_active_text': '#ffffff',
            
            # Кнопки
            'btn_primary_bg': '#0d6efd',
            'btn_primary_text': '#ffffff',
            'btn_primary_hover': '#0b5ed7',
            'btn_secondary_bg': '#6c757d',
            'btn_secondary_text': '#ffffff',
            'btn_secondary_hover': '#5c636a',
            
            # Поля ввода
            'input_bg': '#343a40',
            'input_border': '#6c757d',
            'input_focus': '#0d6efd',
            'input_text': '#ffffff',
            
            # Скроллбары
            'scrollbar_bg': '#495057',
            'scrollbar_thumb': '#6c757d',
            'scrollbar_thumb_hover': '#adb5bd'
        }
        
        fonts = {
            'primary': ('Segoe UI', 9),
            'secondary': ('Segoe UI', 8),
            'heading': ('Segoe UI', 12, 'bold'),
            'message': ('Segoe UI', 11),
            'timestamp': ('Segoe UI', 8),
            'button': ('Segoe UI', 9)
        }
        
        super().__init__('Dark', colors, fonts)

class ThemeManager:
    """Менеджер тем"""
    
    def __init__(self):
        self.themes = {
            'light': LightTheme(),
            'dark': DarkTheme()
        }
        self.current_theme = 'light'
    
    def get_theme(self, theme_name=None):
        """Получить тему"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes['light'])
    
    def set_theme(self, theme_name):
        """Установить тему"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_available_themes(self):
        """Получить список доступных тем"""
        return list(self.themes.keys())
    
    def get_color(self, color_name, theme_name=None):
        """Получить цвет из текущей темы"""
        theme = self.get_theme(theme_name)
        return theme.colors.get(color_name, '#000000')
    
    def get_font(self, font_name, theme_name=None):
        """Получить шрифт из текущей темы"""
        theme = self.get_theme(theme_name)
        return theme.fonts.get(font_name, ('Arial', 9))

