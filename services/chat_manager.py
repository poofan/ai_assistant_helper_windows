#!/usr/bin/env python3
"""
Chat Manager Service
Управление чатами, сохранение и загрузка истории
"""

import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ChatManager:
    """Менеджер для управления чатами и их сохранения"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Инициализация менеджера чатов
        
        Args:
            data_dir: Директория для хранения данных
        """
        self.logger = logging.getLogger(__name__)
        
        # Handle PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle - use executable directory
            base_path = os.path.dirname(sys.executable)
            self.data_dir = Path(base_path) / data_dir
        else:
            # Running as Python script
            self.data_dir = Path(data_dir)
        
        self.chats_file = self.data_dir / "chats.json"
        
        # Создаем директорию если не существует
        self.data_dir.mkdir(exist_ok=True)
        
        # Загружаем существующие чаты
        self.chats = self._load_chats()
        
        self.logger.info(f"ChatManager initialized. Data directory: {self.data_dir}")
    
    def _load_chats(self) -> Dict[str, Dict]:
        """Загрузить чаты из файла"""
        try:
            if self.chats_file.exists():
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    chats = json.load(f)
                    self.logger.info(f"Loaded {len(chats)} chats from {self.chats_file}")
                    return chats
            else:
                self.logger.info("No existing chats file found, starting with empty chats")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading chats: {e}")
            return {}
    
    def _save_chats(self):
        """Сохранить чаты в файл"""
        try:
            with open(self.chats_file, 'w', encoding='utf-8') as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved {len(self.chats)} chats to {self.chats_file}")
        except Exception as e:
            self.logger.error(f"Error saving chats: {e}")
    
    def create_chat(self, chat_id: str, name: str = None) -> Dict:
        """
        Создать новый чат
        
        Args:
            chat_id: Уникальный идентификатор чата
            name: Название чата (если не указано, будет сгенерировано)
            
        Returns:
            Словарь с данными чата
        """
        if chat_id in self.chats:
            self.logger.warning(f"Chat {chat_id} already exists")
            return self.chats[chat_id]
        
        if not name:
            name = f"Chat {len(self.chats) + 1}"
        
        chat_data = {
            "id": chat_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        self.chats[chat_id] = chat_data
        self._save_chats()
        
        self.logger.info(f"Created new chat: {chat_id} - {name}")
        return chat_data
    
    def get_chat(self, chat_id: str) -> Optional[Dict]:
        """Получить чат по ID"""
        return self.chats.get(chat_id)
    
    def get_all_chats(self) -> Dict[str, Dict]:
        """Получить все чаты"""
        return self.chats.copy()
    
    def get_chat_list(self) -> List[Dict]:
        """Получить список чатов для отображения"""
        chat_list = []
        for chat_id, chat_data in self.chats.items():
            chat_list.append({
                "id": chat_id,
                "name": chat_data["name"],
                "created_at": chat_data["created_at"],
                "updated_at": chat_data["updated_at"],
                "message_count": len(chat_data["messages"])
            })
        
        # Сортируем по времени обновления (новые сверху)
        chat_list.sort(key=lambda x: x["updated_at"], reverse=True)
        return chat_list
    
    def add_message(self, chat_id: str, message: Dict):
        """
        Добавить сообщение в чат
        
        Args:
            chat_id: ID чата
            message: Словарь с данными сообщения
        """
        if chat_id not in self.chats:
            self.logger.error(f"Chat {chat_id} not found")
            return
        
        # Добавляем timestamp если его нет
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        # Добавляем ID сообщения если его нет
        if "id" not in message:
            message["id"] = f"msg_{len(self.chats[chat_id]['messages'])}"
        
        self.chats[chat_id]["messages"].append(message)
        self.chats[chat_id]["updated_at"] = datetime.now().isoformat()
        
        self._save_chats()
        self.logger.debug(f"Added message to chat {chat_id}")
    
    def get_messages(self, chat_id: str) -> List[Dict]:
        """Получить все сообщения чата"""
        if chat_id not in self.chats:
            return []
        return self.chats[chat_id]["messages"].copy()
    
    def update_chat_name(self, chat_id: str, new_name: str):
        """Обновить название чата"""
        if chat_id not in self.chats:
            self.logger.error(f"Chat {chat_id} not found")
            return
        
        old_name = self.chats[chat_id]["name"]
        self.chats[chat_id]["name"] = new_name
        self.chats[chat_id]["updated_at"] = datetime.now().isoformat()
        
        self._save_chats()
        self.logger.info(f"Updated chat {chat_id} name: '{old_name}' -> '{new_name}'")
    
    def delete_chat(self, chat_id: str):
        """Удалить чат"""
        if chat_id not in self.chats:
            self.logger.error(f"Chat {chat_id} not found")
            return
        
        chat_name = self.chats[chat_id]["name"]
        del self.chats[chat_id]
        self._save_chats()
        
        self.logger.info(f"Deleted chat {chat_id} - {chat_name}")
    
    def clear_chat_messages(self, chat_id: str):
        """Очистить все сообщения в чате"""
        if chat_id not in self.chats:
            self.logger.error(f"Chat {chat_id} not found")
            return
        
        message_count = len(self.chats[chat_id]["messages"])
        self.chats[chat_id]["messages"] = []
        self.chats[chat_id]["updated_at"] = datetime.now().isoformat()
        
        self._save_chats()
        self.logger.info(f"Cleared {message_count} messages from chat {chat_id}")
    
    def export_chat(self, chat_id: str, format: str = "json") -> str:
        """
        Экспортировать чат в файл
        
        Args:
            chat_id: ID чата
            format: Формат экспорта (json, txt)
            
        Returns:
            Путь к экспортированному файлу
        """
        if chat_id not in self.chats:
            self.logger.error(f"Chat {chat_id} not found")
            return None
        
        chat_data = self.chats[chat_id]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"chat_{chat_id}_{timestamp}.json"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
        elif format == "txt":
            filename = f"chat_{chat_id}_{timestamp}.txt"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Chat: {chat_data['name']}\n")
                f.write(f"Created: {chat_data['created_at']}\n")
                f.write(f"Updated: {chat_data['updated_at']}\n")
                f.write("=" * 50 + "\n\n")
                
                for msg in chat_data['messages']:
                    f.write(f"[{msg.get('timestamp', 'N/A')}] {msg.get('sender', 'Unknown')}: {msg.get('content', '')}\n\n")
        
        else:
            self.logger.error(f"Unsupported export format: {format}")
            return None
        
        self.logger.info(f"Exported chat {chat_id} to {filepath}")
        return str(filepath)
    
    def get_stats(self) -> Dict:
        """Получить статистику чатов"""
        total_chats = len(self.chats)
        total_messages = sum(len(chat["messages"]) for chat in self.chats.values())
        
        return {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "data_directory": str(self.data_dir),
            "chats_file": str(self.chats_file)
        }

