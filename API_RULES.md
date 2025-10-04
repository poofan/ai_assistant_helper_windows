# 🔗 YourSmartScreen API - Правила интеграции

## 📋 Основная информация

**Base URL:** `https://assistpro.site`  
**Протокол:** HTTPS  
**Аутентификация:** JWT Bearer Token

## 🔐 Аутентификация

### Регистрация пользователя
```
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string", 
  "password": "string"
}
```

**Ответ при успехе:**
```json
{
  "message": "Пользователь успешно зарегистрирован",
  "user_id": "uuid"
}
```

### Вход пользователя
```
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Ответ при успехе:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Ответ при ошибке:**
```json
{
  "detail": "Неверное имя пользователя или пароль"
}
```

### Проверка токена
```
GET /auth/verify
Authorization: Bearer YOUR_TOKEN
```

**Ответ при успехе:**
```json
{
  "valid": true,
  "user_id": "uuid",
  "username": "string"
}
```

## 💳 Подписки

### Получение планов подписок
```
GET /subscriptions/plans
Authorization: Bearer YOUR_TOKEN
```

### Покупка подписки
```
POST /subscriptions/purchase
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "plan_id": "string"
}
```

## 🪙 Кредиты

### Получение пакетов кредитов
```
GET /credits/packages
Authorization: Bearer YOUR_TOKEN
```

### Покупка кредитов
```
POST /credits/purchase
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "package_id": "string" OR "credits": number
}
```

## 🤖 AI и чат

### Отправка сообщения
```
POST /chat/send
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "message": "string",
  "previous_response_id": "string" (optional)
}
```

**Ответ:**
```json
{
  "response": "AI ответ",
  "response_id": "uuid",
  "tokens_used": number,
  "model": "string"
}
```

### Анализ изображения
```
POST /openrouter/image/analyze
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

file: image_file
prompt: "string"
model: "openai/gpt-4.1-mini"
```

## 📥 Скачивание

### Получение ссылки для скачивания
```
GET /download/link/{file_id}
Authorization: Bearer YOUR_TOKEN
```

## 📊 Статус коды

| Код | Описание | Действие |
|-----|----------|----------|
| 200 | Успешно | Продолжить |
| 400 | Неверный запрос | Проверить данные |
| 401 | Не авторизован | Обновить токен |
| 402 | Требуется подписка | Показать диалог подписки |
| 403 | Доступ запрещен | Уведомить пользователя |
| 404 | Не найдено | Проверить URL |
| 422 | Ошибка валидации | Исправить данные |
| 429 | Превышен лимит | Подождать и повторить |
| 500 | Ошибка сервера | Повторить позже |

## 🔧 Обработка ошибок

### Типы ошибок авторизации:
- `invalid_credentials` - Неверные данные для входа
- `token_expired` - Токен истек
- `payment_required` - Требуется подписка/кредиты
- `network_error` - Проблемы с сетью
- `unknown_error` - Неизвестная ошибка

### Структура ответа при ошибке:
```json
{
  "success": false,
  "error": "error_type",
  "message": "Описание ошибки",
  "subscription_status": {}, // если payment_required
  "available_plans": [], // если payment_required
  "credit_packages": [], // если payment_required
  "purchase_url": "string" // если payment_required
}
```

## 🚀 Интеграция в приложение

### 1. Обновить base_url в config.ini:
```ini
[api]
base_url = https://assistpro.site
```

### 2. Методы API Client должны возвращать словари:
```python
def login(self, username: str, password: str) -> Dict:
    # Возвращает {"success": bool, "error": str, "message": str}

def verify_token(self) -> Dict:
    # Возвращает {"success": bool, "valid": bool, "user_id": str}

def register(self, username: str, password: str, email: str) -> Dict:
    # Возвращает {"success": bool, "message": str}
```

### 3. Обработка в UI:
- Всегда проверять `result.get("success")`
- При `payment_required` показывать диалог подписки
- При `invalid_credentials` показывать ошибку входа
- При `network_error` предлагать повторить

## 🔒 Безопасность

- Всегда использовать HTTPS
- Сохранять токены в безопасном месте
- Проверять валидность токена при запуске
- Обрабатывать истечение токенов
- Не логировать токены в открытом виде

## 📝 Важные замечания

1. **НЕ МЕНЯТЬ** endpoint для чата: `/openai/chat`
2. **Всегда** проверять статус коды HTTP
3. **Всегда** возвращать словари из API методов
4. **Обрабатывать** все типы ошибок
5. **Использовать** правильные заголовки авторизации
