# Telegram-бот для продажи VPN-ключей (Outline)
https://borislav2515.github.io/r14vpn/

Этот бот позволяет пользователям:
- Узнать, что такое Outline VPN
- Выбрать сервер (Германия/США)
- Сгенерировать себе ключ доступа
- Просматривать свои ключи

В будущем будет добавлена оплата.

## Технологии
- Python 3.8+
- aiogram (Telegram Bot API)
- requests (работа с Outline API)
- sqlite3 (база данных) 

# Управление сервисом gunicorn-vpn (автозапуск backend)

Для управления backend-сервисом (gunicorn) используйте следующие команды:

```
systemctl start gunicorn-vpn    # Запустить сервис
systemctl stop gunicorn-vpn     # Остановить сервис
systemctl restart gunicorn-vpn  # Перезапустить сервис
systemctl status gunicorn-vpn   # Проверить статус сервиса
```

--- 

# Управление сервисом Telegram-бота (vpn-bot)

Для управления Telegram-ботом используйте следующие команды:

```
systemctl start vpn-bot    # Запустить бота
systemctl stop vpn-bot     # Остановить бота
systemctl restart vpn-bot  # Перезапустить бота
systemctl status vpn-bot   # Проверить статус бота
```

--- 
