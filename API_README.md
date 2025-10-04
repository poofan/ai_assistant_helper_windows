# 🚀 YourSmartScreen API

## 📋 Обзор

YourSmartScreen API - это RESTful API для системы подписок, кредитов и AI-ассистента с админской панелью.

**Base URL:** `https://assistpro.site`

## 🔗 Быстрые ссылки

- 📖 **[Полная документация API](API_CURL_REFERENCE.md)** - Подробные примеры curl команд
- ⚡ **[Быстрая справка](API_QUICK_REFERENCE.md)** - Краткий список эндпоинтов
- 📊 **[Postman коллекция](YourSmartScreen_API.postman_collection.json)** - Готовая коллекция для тестирования
- 🌍 **[Postman Environment](YourSmartScreen_Environment.postman_environment.json)** - Переменные окружения

## 🎯 Основные возможности

### 🔐 Аутентификация
- Регистрация и вход пользователей
- JWT токены
- Проверка токенов

### 💳 Подписки
- Планы подписок (basic, pro, enterprise)
- Покупка подписок
- Управление подписками

### 🪙 Кредиты
- Пакеты кредитов
- Произвольная покупка кредитов
- Отслеживание использования

### 🤖 AI и чат
- Отправка сообщений
- Анализ изображений
- История чатов

### 📥 Скачивание
- Безопасные ссылки для скачивания
- Версионирование файлов
- Pre-signed URLs

### 🔒 Админская панель
- Управление настройками
- Создание администраторов
- Мониторинг системы

## 🚀 Быстрый старт

### 1. Регистрация пользователя
```bash
curl -X POST "https://assistpro.site/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "pass"}'
```

### 2. Вход
```bash
curl -X POST "https://assistpro.site/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### 3. Отправка сообщения
```bash
curl -X POST "https://assistpro.site/chat/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет!"}'
```

## 📊 Статус коды

| Код | Описание |
|-----|----------|
| 200 | Успешно |
| 400 | Неверный запрос |
| 401 | Не авторизован |
| 402 | Требуется подписка |
| 403 | Доступ запрещен |
| 404 | Не найдено |
| 422 | Ошибка валидации |
| 429 | Превышен лимит |
| 500 | Ошибка сервера |

## 🔧 Интеграция

### JavaScript/TypeScript
```javascript
const API_BASE_URL = 'https://assistpro.site';

// Авторизация
const login = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return response.json();
};

// Отправка сообщения
const sendMessage = async (token, message) => {
  const response = await fetch(`${API_BASE_URL}/chat/send`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
  return response.json();
};
```

### Python
```python
import requests

API_BASE_URL = 'https://assistpro.site'

# Авторизация
def login(username, password):
    response = requests.post(f'{API_BASE_URL}/auth/login', json={
        'username': username,
        'password': password
    })
    return response.json()

# Отправка сообщения
def send_message(token, message):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{API_BASE_URL}/chat/send', 
                           json={'message': message}, 
                           headers=headers)
    return response.json()
```

## 🛠️ Инструменты разработки

### Postman
1. Импортируйте `YourSmartScreen_API.postman_collection.json`
2. Импортируйте `YourSmartScreen_Environment.postman_environment.json`
3. Выберите environment "YourSmartScreen Environment"
4. Начните тестирование с эндпоинта "Регистрация пользователя"

### Swagger UI
Откройте `https://assistpro.site/docs` в браузере для интерактивной документации.

## 🔒 Безопасность

- Все API эндпоинты используют HTTPS
- JWT токены для аутентификации
- Pre-signed URLs для безопасного скачивания
- Валидация всех входных данных
- Rate limiting для защиты от злоупотреблений

## 📈 Мониторинг

- Health check: `GET /health`
- Логирование всех запросов
- Метрики использования
- Алерты при ошибках

## 🆘 Поддержка

- 📧 Email: support@assistpro.site
- 📖 Документация: [API_CURL_REFERENCE.md](API_CURL_REFERENCE.md)
- 🐛 Баги: Создайте issue в репозитории

---

**🎉 Готово к использованию!** Начните с регистрации пользователя и изучите полную документацию.
