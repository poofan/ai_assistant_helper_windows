"""
Markdown Renderer - Simple Markdown to tkinter Text widget renderer
"""

import re
import tkinter as tk
from typing import Dict, List, Tuple

class MarkdownRenderer:
    """Simple Markdown renderer for tkinter Text widget"""
    
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
        self.theme_manager = None  # Will be set later
        
    def set_theme_manager(self, theme_manager):
        """Set theme manager for styling"""
        self.theme_manager = theme_manager
        
    def render_markdown(self, markdown_text: str, start_index: str = tk.END) -> None:
        """Render markdown text to tkinter Text widget"""
        if not markdown_text:
            return
            
        # Debug: print(f"DEBUG: Rendering markdown text: {markdown_text[:200]}...")
        
        # Parse markdown and apply formatting
        self._parse_and_insert(markdown_text, start_index)
    
    def _parse_and_insert(self, text: str, start_index: str) -> None:
        """Parse markdown text and insert with formatting"""
        lines = text.split('\n')
        current_index = start_index
        
        for line in lines:
            if not line.strip():
                # Empty line
                self.text_widget.insert(current_index, '\n')
                current_index = tk.END
                continue
                
            # Check for different markdown elements
            if line.startswith('# '):
                # H1 header
                self._insert_header(line[2:], 1, current_index)
            elif line.startswith('## '):
                # H2 header
                self._insert_header(line[3:], 2, current_index)
            elif line.startswith('### '):
                # H3 header
                self._insert_header(line[4:], 3, current_index)
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet list
                self._insert_bullet(line[2:], current_index)
            elif line.startswith('1. ') or re.match(r'^\d+\. ', line):
                # Numbered list
                self._insert_numbered(line, current_index)
            elif line.startswith('```'):
                # Code block start/end - skip for now
                self.text_widget.insert(current_index, line + '\n', 'code_block')
            elif line.startswith('`') and line.endswith('`') and len(line) > 2:
                # Inline code
                self._insert_inline_code(line, current_index)
            else:
                # Regular text - check for inline formatting
                self._insert_formatted_text(line, current_index)
            
            current_index = tk.END
    
    def _insert_header(self, text: str, level: int, start_index: str) -> None:
        """Insert header with appropriate formatting"""
        tag_name = f'header_{level}'
        self.text_widget.insert(start_index, text + '\n', tag_name)
        
        # Configure header tag if theme manager is available
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            font_size = 14 - level  # H1=13, H2=12, H3=11
            self.text_widget.tag_configure(tag_name, 
                                         font=(theme.fonts['primary'][0], font_size, 'bold'),
                                         foreground=theme.colors.get('header_color', theme.colors['text_primary']))
    
    def _insert_bullet(self, text: str, start_index: str) -> None:
        """Insert bullet point"""
        self.text_widget.insert(start_index, '• ', 'bullet')
        self._insert_formatted_text(text, tk.END)
        self.text_widget.insert(tk.END, '\n')
        
        # Configure bullet tag
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            self.text_widget.tag_configure('bullet', 
                                         font=(theme.fonts['primary'][0], theme.fonts['primary'][1], 'bold'),
                                         foreground=theme.colors.get('bullet_color', theme.colors['text_primary']))
    
    def _insert_numbered(self, text: str, start_index: str) -> None:
        """Insert numbered list item"""
        # Extract number and text
        match = re.match(r'^(\d+\.)\s*(.*)', text)
        if match:
            number, content = match.groups()
            self.text_widget.insert(start_index, number + ' ', 'number')
            self._insert_formatted_text(content, tk.END)
            self.text_widget.insert(tk.END, '\n')
            
            # Configure number tag
            if self.theme_manager:
                theme = self.theme_manager.get_theme()
                self.text_widget.tag_configure('number', 
                                             font=(theme.fonts['primary'][0], theme.fonts['primary'][1], 'bold'),
                                             foreground=theme.colors.get('number_color', theme.colors['text_primary']))
    
    def _insert_inline_code(self, text: str, start_index: str) -> None:
        """Insert inline code"""
        # Remove backticks
        code_text = text[1:-1]
        self.text_widget.insert(start_index, code_text, 'inline_code')
        
        # Configure inline code tag
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            self.text_widget.tag_configure('inline_code', 
                                         font=(theme.fonts['primary'][0], theme.fonts['primary'][1], 'normal'),
                                         background=theme.colors.get('code_bg', '#f0f0f0'),
                                         foreground=theme.colors.get('code_text', '#d63384'),
                                         relief='flat',
                                         borderwidth=1)
    
    def _insert_formatted_text(self, text: str, start_index: str) -> None:
        """Insert text with inline formatting (bold, italic, links)"""
        # Split text by formatting markers
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
        
        for part in parts:
            if not part:
                continue
                
            if part.startswith('**') and part.endswith('**'):
                # Bold text
                bold_text = part[2:-2]
                self.text_widget.insert(start_index, bold_text, 'bold')
                if self.theme_manager:
                    theme = self.theme_manager.get_theme()
                    self.text_widget.tag_configure('bold', 
                                                 font=(theme.fonts['primary'][0], theme.fonts['primary'][1], 'bold'),
                                                 foreground=theme.colors['text_primary'])
            elif part.startswith('*') and part.endswith('*') and len(part) > 2:
                # Italic text
                italic_text = part[1:-1]
                self.text_widget.insert(start_index, italic_text, 'italic')
                if self.theme_manager:
                    theme = self.theme_manager.get_theme()
                    self.text_widget.tag_configure('italic', 
                                                 font=(theme.fonts['primary'][0], theme.fonts['primary'][1], 'italic'),
                                                 foreground=theme.colors['text_primary'])
            elif part.startswith('`') and part.endswith('`') and len(part) > 2:
                # Inline code (already handled above, but just in case)
                code_text = part[1:-1]
                self.text_widget.insert(start_index, code_text, 'inline_code')
            else:
                # Regular text
                self.text_widget.insert(start_index, part)
        
        # Add newline at the end
        self.text_widget.insert(tk.END, '\n')
