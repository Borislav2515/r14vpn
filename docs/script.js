document.getElementById('keys-btn').onclick = showKeys;
document.getElementById('stats-btn').onclick = showStats;
document.getElementById('support-btn').onclick = showSupport;

// ВАЖНО: Укажите здесь публичный HTTPS-адрес вашего backend!
// Например:
// const API_BASE = "https://your-backend.example.com";
const API_BASE = "https://your-backend.example.com";

function showKeys() {
  document.getElementById('main-content').innerHTML = `
    <h2>Ваши ключи</h2>
    <div id="keys-list">Загрузка...</div>
    <button class="primary" id="get-key-btn">Получить новый ключ</button>
  `;
  fetch(`${API_BASE}/api/keys`)
    .then(r => r.json())
    .then(data => {
      if (data.keys && data.keys.length > 0) {
        document.getElementById('keys-list').innerHTML = data.keys.map(k => `<div class="card"><b>${k.name}</b><br>Ссылка: <a href="${k.accessUrl}" target="_blank">${k.accessUrl}</a></div>`).join('');
      } else {
        document.getElementById('keys-list').innerHTML = '<div>Нет ключей</div>';
      }
    });
  document.getElementById('get-key-btn').onclick = getKey;
}

function getKey() {
  const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const username = tgUser?.username || `user_${tgUser?.id || 1}`;
  const user_id = tgUser?.id || 1;
  fetch(`${API_BASE}/api/get_key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, user_id })
  })
    .then(r => r.json())
    .then(data => {
      if (data.key) {
        alert('Ключ успешно создан!');
        showKeys();
      } else {
        alert('Ошибка при создании ключа');
      }
    });
}

function showStats() {
  document.getElementById('main-content').innerHTML = '<h2>Статистика</h2><div id="stats">Загрузка...</div>';
  fetch(`${API_BASE}/api/stats`)
    .then(r => r.json())
    .then(data => {
      document.getElementById('stats').innerHTML = `
        <div class="card">
          <b>Трафик:</b> ${data.traffic || 0} МБ<br>
          <b>Активных ключей:</b> ${data.active_keys || 0}
        </div>
      `;
    });
}

function showSupport() {
  document.getElementById('main-content').innerHTML = '<h2>Поддержка</h2><div class="card">По всем вопросам пишите: <a href="mailto:support@example.com">support@example.com</a></div>';
}

// По умолчанию показываем ключи
showKeys(); 