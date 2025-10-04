"""
API Client - Handles communication with the YourSmartScreen API
"""

import requests
import json
import logging
from pathlib import Path
from typing import Dict, Optional

class APIClient:
    """Client for YourSmartScreen API"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.base_url = config.get("api", "base_url", "http://147.45.227.57")
        self.timeout = config.getint("api", "timeout", 30)
        self.auth_token = None
        
        # Session for connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "AI-Chat-Messenger/1.0"
        })
    
    def login(self, username: str, password: str) -> bool:
        """Login user and get authentication token"""
        try:
            url = f"{self.base_url}/auth/login"
            data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get("access_token"):
                self.auth_token = result.get("access_token")
                if self.auth_token:
                    self.session.headers["Authorization"] = f"Bearer {self.auth_token}"
                    self.save_auth_token()
                    self.logger.info("Login successful")
                    return True
            
            self.logger.error(f"Login failed: {result.get('detail', 'Unknown error')}")
            return False
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Login request failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def register(self, username: str, password: str, email: str = None) -> bool:
        """Register new user"""
        try:
            url = f"{self.base_url}/auth/register"
            data = {
                "username": username,
                "password": password
            }
            if email:
                data["email"] = email
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            # Проверяем успешную регистрацию по сообщению
            message = result.get("message", "")
            if "успешно зарегистрирован" in message.lower() or "successfully registered" in message.lower():
                self.logger.info("Registration successful")
                return True
            
            self.logger.error(f"Registration failed: {message}")
            return False
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Registration request failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False
    
    def logout(self):
        """Logout user and clear token"""
        self.auth_token = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        self.clear_auth_token()
        self.logger.info("Logged out")
    
    def verify_token(self) -> Dict:
        """Verify the current authentication token"""
        try:
            if not self.auth_token:
                return {"success": False, "valid": False, "error": "No token available"}
            
            url = f"{self.base_url}/auth/verify"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "valid": result.get("valid", False),
                    "user_id": result.get("user_id")
                }
            else:
                return {
                    "success": False,
                    "valid": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Token verification request failed: {e}")
            return {"success": False, "valid": False, "error": str(e)}
        except Exception as e:
            self.logger.error(f"Token verification error: {e}")
            return {"success": False, "valid": False, "error": str(e)}
    
    def send_message(self, message: str, previous_response_id: Optional[str] = None) -> Dict:
        """Send a chat message to the API"""
        try:
            if not self.auth_token:
                return {"success": False, "error": "Not authenticated"}
            
            url = f"{self.base_url}/chat/send"
            # Add system prompt for poker bot context
            system_prompt = """Ты - ИИ-агент для игры в покер. Твоя задача:
1. Анализировать скриншоты покерных столов
2. Выбирать оптимальные действия (fold/call/raise)
3. Отвечать на вопросы о покере
4. Помогать с игровой стратегией

Отвечай кратко и по делу. Для действий в покере используй только JSON формат: {"action": "button_fold"}, {"action": "button_call"}, {"action": "button_raise"}."""

            data = {
                "message": message,
                "system_prompt": system_prompt
            }
            
            if previous_response_id:
                data["previous_response_id"] = previous_response_id
            
            response = self.session.post(url, json=data)
            
            # Детальное логирование для отладки
            self.logger.info(f"Send message request - Status: {response.status_code}")
            self.logger.info(f"Send message request - Headers: {dict(response.headers)}")
            self.logger.info(f"Send message request - Response text: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            if result.get("response"):
                return {
                    "success": True,
                    "message": result.get("response", ""),
                    "response_id": result.get("response_id"),
                    "tokens_used": result.get("tokens_used"),
                    "model": result.get("model")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("detail", "Unknown error")
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Send message request failed: {e}")
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Send message error: {e}")
            return {"success": False, "error": f"Error: {str(e)}"}
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict:
        """Analyze an image using the API"""
        try:
            if not self.auth_token:
                return {"success": False, "error": "Not authenticated"}
            
            url = f"{self.base_url}/openrouter/image/analyze"
            
            # Prepare multipart form data
            with open(image_path, 'rb') as image_file:
                files = {
                    'file': ('screenshot.png', image_file, 'image/png')
                }
                data = {
                    'prompt': prompt,
                    'model': 'openai/gpt-4.1-mini'
                }
                
                # Use direct requests.post for multipart data
                headers = {
                    'Authorization': f'Bearer {self.auth_token}'
                }
                
                response = requests.post(url, files=files, data=data, headers=headers)
                
                # Детальное логирование для отладки
                self.logger.info(f"Image analysis request - Status: {response.status_code}")
                self.logger.info(f"Image analysis request - Headers: {dict(response.headers)}")
                self.logger.info(f"Image analysis request - Response text: {response.text}")
                
                response.raise_for_status()
                
                result = response.json()
                if result.get("analysis"):
                    return {
                        "success": True,
                        "message": result.get("analysis", ""),
                        "model": result.get("model"),
                        "tokens_used": result.get("tokens_used"),
                        "processing_time": result.get("processing_time")
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Analysis failed")
                    }
                    
        except FileNotFoundError:
            self.logger.error(f"Image file not found: {image_path}")
            return {"success": False, "error": "Image file not found"}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Image analysis request failed: {e}")
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Image analysis error: {e}")
            return {"success": False, "error": f"Error: {str(e)}"}
    
    def save_auth_token(self):
        """Save authentication token to file"""
        try:
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            
            token_file = config_dir / "auth_token.json"
            with open(token_file, 'w') as f:
                json.dump({"token": self.auth_token}, f)
                
        except Exception as e:
            self.logger.error(f"Failed to save auth token: {e}")
    
    def load_auth_token(self) -> bool:
        """Load authentication token from file"""
        try:
            token_file = Path("config") / "auth_token.json"
            if token_file.exists():
                with open(token_file, 'r') as f:
                    data = json.load(f)
                    self.auth_token = data.get("token")
                    if self.auth_token:
                        self.session.headers["Authorization"] = f"Bearer {self.auth_token}"
                        return True
        except Exception as e:
            self.logger.error(f"Failed to load auth token: {e}")
        return False
    
    def clear_auth_token(self):
        """Clear saved authentication token"""
        try:
            token_file = Path("config") / "auth_token.json"
            if token_file.exists():
                token_file.unlink()
        except Exception as e:
            self.logger.error(f"Failed to clear auth token: {e}")
