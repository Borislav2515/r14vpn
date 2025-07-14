# R14-VPN - Система управления VPN

Современная система управления VPN с Telegram-ботом и мобильным веб-приложением.

## 🚀 Возможности

- **Telegram-бот** для управления VPN ключами
- **Мобильное веб-приложение** с современным дизайном
- **API** для интеграции с Outline Manager
- **Управление ключами**: создание, просмотр, удаление
- **Статистика** использования
- **Адаптивный дизайн** для мобильных устройств

## 📱 Новые функции

### Мобильная адаптация
- ✅ Современный дизайн с градиентами и анимациями
- ✅ Адаптивная верстка для всех устройств
- ✅ Поддержка темной темы
- ✅ Улучшенная навигация с иконками

### Управление ключами
- ✅ Кнопка удаления ключа справа от названия
- ✅ Копирование ссылок в буфер обмена
- ✅ Подтверждение удаления
- ✅ Уведомления о действиях

### Улучшения UI/UX
- ✅ Красивые карточки с эффектами
- ✅ Анимации и переходы
- ✅ Современная типографика (Inter)
- ✅ Улучшенная статистика

## 🛠 Установка и настройка

### 1. Клонирование и настройка
```bash
git clone https://github.com/Borislav2515/r14vpn.git
cd r14vpn
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка конфигурации
Отредактируйте `bot_config.py`:
```python
BOT_TOKEN = "ваш_токен_бота"
OUTLINE_SERVERS = [
    {
        "id": "server1",
        "name": "Германия",
        "api_url": "https://ваш_сервер:port/api"
    }
]
```

### 4. Запуск на сервере

#### Backend (Flask)
```bash
# Создание systemd сервиса
sudo tee /etc/systemd/system/gunicorn-vpn.service > /dev/null << EOF
[Unit]
Description=Gunicorn instance to serve vpn_webapp
After=network.target

[Service]
User=root
WorkingDirectory=/opt/r14vpn
Environment="PATH=/opt/r14vpn/venv/bin"
ExecStart=/opt/r14vpn/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 webapp_backend:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-vpn
sudo systemctl start gunicorn-vpn
```

#### Telegram Bot
```bash
# Создание systemd сервиса
sudo tee /etc/systemd/system/vpn-bot.service > /dev/null << EOF
[Unit]
Description=VPN Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/opt/r14vpn
Environment="PATH=/opt/r14vpn/venv/bin"
ExecStart=/opt/r14vpn/venv/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable vpn-bot
sudo systemctl start vpn-bot
```

#### Nginx конфигурация
```nginx
server {
    listen 80;
    server_name _;

    # API проксирование
    location /api {
        proxy_pass http://127.0.0.1:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Статические файлы miniapp
    location / {
        root /opt/r14vpn/miniapp;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

## 📋 Управление сервисами

```bash
# Проверка статуса
sudo systemctl status gunicorn-vpn
sudo systemctl status vpn-bot
sudo systemctl status nginx

# Перезапуск
sudo systemctl restart gunicorn-vpn
sudo systemctl restart vpn-bot
sudo systemctl reload nginx

# Просмотр логов
sudo journalctl -u gunicorn-vpn -f
sudo journalctl -u vpn-bot -f
sudo tail -f /var/log/nginx/error.log
```

## 🌐 Доступ

- **WebApp**: http://178.250.191.242/
- **API**: http://178.250.191.242/api/keys
- **Telegram Bot**: @ваш_бот

## 🔧 API Endpoints

- `GET /api/keys` - Получить список ключей
- `POST /api/get_key` - Создать новый ключ
- `POST /api/delete_key` - Удалить ключ
- `GET /api/stats` - Получить статистику

## 📱 Особенности мобильной версии

- **Адаптивный дизайн** для всех размеров экранов
- **Touch-friendly** интерфейс
- **Быстрые действия** (копирование, удаление)
- **Современные анимации** и переходы
- **Поддержка жестов** и свайпов

## 🎨 Дизайн

- **Цветовая схема**: Градиенты синего и фиолетового
- **Шрифт**: Inter (Google Fonts)
- **Эффекты**: Backdrop blur, тени, анимации
- **Иконки**: Emoji для лучшей совместимости
- **Темы**: Поддержка светлой и темной темы

## 🔒 Безопасность

- Проверка подписи Telegram WebApp (рекомендуется)
- Валидация входных данных
- Безопасное удаление ключей
- Логирование действий

## 📞 Поддержка

По всем вопросам обращайтесь: support@example.com 