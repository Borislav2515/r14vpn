from db import get_expired_keys, mark_key_deleted
from bot_config import OUTLINE_SERVERS
from outline_api import delete_access_key
from datetime import datetime

# Получаем все просроченные ключи
expired_keys = get_expired_keys()

# Сопоставление серверов по id
servers_map = {s['id']: s for s in OUTLINE_SERVERS}

for key in expired_keys:
    db_id, user_id, server_id, access_key_id, expires_at = key
    server = servers_map.get(server_id)
    if not server:
        print(f"[!] Сервер {server_id} не найден для ключа {access_key_id}")
        continue
    print(f"Удаляю ключ {access_key_id} (user {user_id}) на сервере {server['name']}...")
    ok = delete_access_key(server['api_url'], access_key_id)
    if ok:
        print(f"[+] Ключ {access_key_id} удалён")
        mark_key_deleted(db_id)
    else:
        print(f"[!] Не удалось удалить ключ {access_key_id}") 