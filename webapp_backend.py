from flask import Flask, send_from_directory, request, jsonify
from db import get_keys, add_key, add_user
from outline_api import create_access_key, get_access_keys
from bot_config import OUTLINE_SERVERS
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/webapp')
def webapp():
    return send_from_directory(os.path.dirname(__file__), 'webapp.html')

@app.route('/webapp-api/my-keys', methods=['POST'])
def api_my_keys():
    data = request.get_json()
    # В реальном проекте нужно проверять подпись initData!
    user_id = parse_user_id(data.get('initData'))
    if not user_id:
        return jsonify({'keys': []})
    keys = get_keys(user_id)
    result = []
    for server in OUTLINE_SERVERS:
        server_id = server['id']
        real_keys = get_access_keys(server['api_url'])
        real_keys_map = {k['id']: k for k in real_keys} if real_keys else dict()
        for s_id, key_id, url, created, expires_at in keys:
            if s_id == server_id and key_id in real_keys_map:
                used_bytes = real_keys_map[key_id].get('usedBytes', 0)
                result.append({
                    'server': server['name'],
                    'created': created[:16],
                    'url': url,
                    'usedBytes': used_bytes,
                    'expiresAt': expires_at
                })
    return jsonify({'keys': result})

@app.route('/webapp-api/generate-key', methods=['POST'])
def api_generate_key():
    data = request.get_json()
    # В реальном проекте нужно проверять подпись initData!
    user_id = parse_user_id(data.get('initData'))
    username = parse_username(data.get('initData')) or f'user_{user_id}'
    if not user_id:
        return jsonify({'success': False, 'error': 'auth'})
    # По умолчанию первый сервер
    server = OUTLINE_SERVERS[0]
    res = create_access_key(server['api_url'], name=username)
    if res and 'id' in res and 'accessUrl' in res:
        # expires_at = now + 30 дней
        from datetime import datetime, timedelta
        expires_at = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        add_key(user_id, server['id'], res['id'], res['accessUrl'], expires_at=expires_at)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'api'})

@app.route('/api/keys', methods=['GET'])
def api_keys():
    # Для простоты: user_id=1 (можно доработать под авторизацию)
    user_id = 1
    keys = get_keys(user_id)
    result = []
    for server in OUTLINE_SERVERS:
        server_id = server['id']
        real_keys = get_access_keys(server['api_url'])
        real_keys_map = {k['id']: k for k in real_keys} if real_keys else dict()
        for s_id, key_id, url, created, expires_at in keys:
            if s_id == server_id and key_id in real_keys_map:
                used_bytes = real_keys_map[key_id].get('usedBytes', 0)
                result.append({
                    'name': server['name'],
                    'accessUrl': url,
                    'created': created[:16],
                    'expiresAt': expires_at,
                    'usedBytes': used_bytes
                })
    return jsonify({'keys': result})

@app.route('/api/get_key', methods=['POST'])
def api_get_key():
    data = request.get_json()
    user_id = data.get('user_id', 1)
    username = data.get('username', f'user_{user_id}')
    server = OUTLINE_SERVERS[0]
    res = create_access_key(server['api_url'], name=username)
    if res and 'id' in res and 'accessUrl' in res:
        from datetime import datetime, timedelta
        expires_at = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        add_key(user_id, server['id'], res['id'], res['accessUrl'], expires_at=expires_at)
        return jsonify({'key': res['accessUrl']})
    return jsonify({'error': 'api'}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    user_id = 1
    keys = get_keys(user_id)
    total_traffic = 0
    active_keys = 0
    for server in OUTLINE_SERVERS:
        real_keys = get_access_keys(server['api_url'])
        real_keys_map = {k['id']: k for k in real_keys} if real_keys else dict()
        for s_id, key_id, url, created, expires_at in keys:
            if s_id == server['id'] and key_id in real_keys_map:
                used_bytes = real_keys_map[key_id].get('usedBytes', 0)
                total_traffic += used_bytes
                active_keys += 1
    return jsonify({'traffic': round(total_traffic / 1024 / 1024, 2), 'active_keys': active_keys})

def parse_user_id(init_data):
    # В реальном проекте нужно парсить и проверять подпись initData!
    # Здесь для теста просто ищем user.id
    import urllib.parse
    if not init_data:
        return None
    params = urllib.parse.parse_qs(init_data)
    user = params.get('user')
    if user:
        import json
        try:
            user_obj = json.loads(user[0])
            return user_obj.get('id')
        except Exception:
            return None
    return None

def parse_username(init_data):
    import urllib.parse
    if not init_data:
        return None
    params = urllib.parse.parse_qs(init_data)
    user = params.get('user')
    if user:
        import json
        try:
            user_obj = json.loads(user[0])
            return user_obj.get('username')
        except Exception:
            return None
    return None

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True) 