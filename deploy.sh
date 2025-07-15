#!/bin/bash

# Скрипт для автоматического деплоя R14-VPN на сервер
# Использование: ./deploy.sh

echo "🚀 Начинаем деплой R14-VPN..."

# Проверяем, что мы в правильной директории
if [ ! -f "bot.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой папки проекта"
    exit 1
fi

# Настройки сервера
SERVER_IP="178.250.191.242"
SERVER_PATH="/opt/r14vpn"
SERVER_USER="root"

echo "📁 Копируем файлы на сервер..."

# Копируем всю папку miniapp (синхронизация)
echo "📱 Синхронизируем miniapp..."
rsync -av --delete miniapp/ $SERVER_USER@$SERVER_IP:$SERVER_PATH/miniapp/

# Копируем backend файлы
echo "🔧 Копируем backend..."
scp webapp_backend.py db.py bot.py $SERVER_USER@$SERVER_IP:$SERVER_PATH/

# Устанавливаем права
echo "🔐 Устанавливаем права..."
ssh $SERVER_USER@$SERVER_IP "chown -R www-data:www-data $SERVER_PATH/miniapp && chmod -R 755 $SERVER_PATH/miniapp"

# Перезапускаем сервисы
echo "🔄 Перезапускаем сервисы..."
ssh $SERVER_USER@$SERVER_IP "systemctl restart gunicorn-vpn && systemctl restart vpn-bot && systemctl reload nginx"

# Проверяем статус
echo "✅ Проверяем статус сервисов..."
ssh $SERVER_USER@$SERVER_IP "systemctl status gunicorn-vpn --no-pager -l && echo '---' && systemctl status vpn-bot --no-pager -l && echo '---' && systemctl status nginx --no-pager -l"

echo "🎉 Деплой завершен!"
echo "🌐 WebApp доступен по адресу: http://$SERVER_IP/"
echo "🔗 API доступен по адресу: http://$SERVER_IP/api/keys" 