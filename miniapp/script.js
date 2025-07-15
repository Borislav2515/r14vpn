// Инициализация навигации
document.getElementById('keys-btn').onclick = showKeys;
document.getElementById('stats-btn').onclick = showStats;
document.getElementById('support-btn').onclick = showSupport;

// API конфигурация
const API_BASE = "https://r14-vpn.ru/api";

// Функция для обновления активной кнопки навигации
function updateActiveNav(activeBtnId) {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  document.getElementById(activeBtnId).classList.add('active');
}

// Функция для показа трафика или empty state
function renderTrafficOrEmpty(keys) {
  const main = document.getElementById('main-content');
  if (keys && keys.length > 0) {
    // Показываем трафик и список ключей
    main.innerHTML = `
      <div class="traffic__inner">
        <div class="card traffic__card">
          <div class="traffic__content">
            <div class="traffic__header">
              <div class="traffic__icon">📈</div>
              <div class="traffic__info">
                <span class="traffic__label">Использование трафика</span>
                <div class="traffic__amount">
                  <span class="used">15.2 ГБ</span>
                  <span class="separator">/</span>
                  <span class="limit">50 ГБ</span>
                </div>
                <div class="traffic__progress">
                  <div class="progress__bar">
                    <div class="progress__fill" style="width: 30%;"></div>
                  </div>
                  <span class="remaining">34.8 ГБ осталось</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <h2>Ваши ключи</h2>
      <div id="keys-list">Загрузка...</div>
      <button class="primary" id="get-key-btn">
        <span>🔑 Получить новый ключ</span>
      </button>
    `;
    // Отрисовываем список ключей
    const keysList = document.getElementById('keys-list');
    if (keys && keys.length > 0) {
      keysList.innerHTML = keys.map(k => `
        <div class="card key-card">
          <div class="key-info">
            <div class="key-name">${k.name}</div>
            <div class="key-url">
              <a href="${k.accessUrl}" target="_blank" onclick="copyToClipboard('${k.accessUrl}')">
                ${k.accessUrl}
              </a>
            </div>
            <div style="font-size: 11px; color: #999; margin-top: 8px;">
              Истекает: ${k.expiresAt}
            </div>
            <div class="btn-wrap">
              <button class="delete-btn" onclick="deleteKey('${k.name}')">Удалить</button>
            </div>
          </div>
        </div>
      `).join('');
    } else {
      keysList.innerHTML = '<div class="empty-state">У вас пока нет ключей</div>';
    }
    // Кнопка создания ключа
    const btn = document.getElementById('get-key-btn');
    if (btn) btn.onclick = getKey;
  } else {
    // Показываем empty state
    main.innerHTML = `
      <div class="traffic__inner">
        <div class="card traffic__card">
          <div class="empty__state">
            <div class="empty__state__image" style="font-size: 3rem;">📉</div>
            <h4 class="empty__state__title">Нет данных по трафику</h4>
            <p class="empty__state__text">Подключитесь к VPN, чтобы увидеть статистику.</p>
            <button class="empty__state__btn">Создать VPN-ключ</button>
          </div>
        </div>
      </div>
    `;
    const emptyBtn = document.querySelector('.empty__state__btn');
    if (emptyBtn) emptyBtn.onclick = getKey;
  }
}

// Функция для показа ключей
function showKeys() {
  updateActiveNav('keys-btn');
  
  // Новый вызов: сначала показываем трафик/empty state
  fetch(`${API_BASE}/keys`)
    .then(r => r.json())
    .then(data => {
      renderTrafficOrEmpty(data.keys);
      // Далее можно отрисовать список ключей ниже, если нужно
    })
    .catch(error => {
      console.error('Ошибка загрузки ключей:', error);
      renderTrafficOrEmpty([]);
    });
  // Удаляю лишний вызов document.getElementById('get-key-btn').onclick = getKey;
}

// Функция для создания нового ключа
function getKey(e) {
  // Получаем кнопку, с которой вызвана функция
  const btn = e?.target || document.getElementById('get-key-btn') || document.querySelector('.empty__state__btn');
  if (!btn) return;

  const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const username = tgUser?.username || `user_${tgUser?.id || 1}`;
  const user_id = tgUser?.id || 1;

  const originalText = btn.innerHTML;
  btn.innerHTML = '<span>⏳ Создание...</span>';
  btn.disabled = true;

  fetch(`${API_BASE}/get_key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, user_id })
  })
    .then(r => r.json())
    .then(data => {
      if (data.key) {
        showNotification('Ключ успешно создан!', 'success');
        showKeys(); // сразу обновляем список ключей
      } else {
        showNotification('Ошибка при создании ключа', 'error');
      }
    })
    .catch(error => {
      console.error('Ошибка создания ключа:', error);
      showNotification('Ошибка при создании ключа', 'error');
    })
    .finally(() => {
      btn.innerHTML = originalText;
      btn.disabled = false;
    });
}

// Функция для удаления ключа
function deleteKey(keyName) {
  if (!confirm(`Вы уверены, что хотите удалить ключ "${keyName}"?`)) {
    return;
  }
  
  const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const user_id = tgUser?.id || 1;
  
  fetch(`${API_BASE}/delete_key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key_name: keyName, user_id })
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        showNotification('Ключ успешно удален!', 'success');
        showKeys();
      } else {
        showNotification('Ошибка при удалении ключа', 'error');
      }
    })
    .catch(error => {
      console.error('Ошибка удаления ключа:', error);
      showNotification('Ошибка при удалении ключа', 'error');
    });
}

// Функция для копирования в буфер обмена
function copyToClipboard(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      showNotification('Ссылка скопирована!', 'success');
    }).catch(() => {
      showNotification('Ошибка копирования', 'error');
    });
  } else {
    // Fallback для старых браузеров
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    showNotification('Ссылка скопирована!', 'success');
  }
}

// Функция для показа статистики
function showStats() {
  updateActiveNav('stats-btn');
  
  document.getElementById('main-content').innerHTML = `
    <h2>Статистика</h2>
    <div id="stats" class="loading">Загрузка...</div>
  `;
  
  fetch(`${API_BASE}/stats`)
    .then(r => r.json())
    .then(data => {
      document.getElementById('stats').innerHTML = `
        <div class="stats-card">
          <div class="stat-item">
            <div class="stat-value">${data.traffic || 0}</div>
            <div class="stat-label">МБ трафика</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">${data.active_keys || 0}</div>
            <div class="stat-label">Активных ключей</div>
          </div>
        </div>
        <div class="card">
          <div style="text-align: center; color: #666; font-size: 14px;">
            📊 Статистика использования VPN
          </div>
        </div>
      `;
    })
    .catch(error => {
      console.error('Ошибка загрузки статистики:', error);
      document.getElementById('stats').innerHTML = '<div class="empty-state">Ошибка загрузки статистики</div>';
    });
}

// Функция для показа поддержки
function showSupport() {
  updateActiveNav('support-btn');
  
  document.getElementById('main-content').innerHTML = `
    <h2>Поддержка</h2>
    <div class="card support-card">
      <div style="font-size: 48px; margin-bottom: 16px;">💬</div>
      <div style="font-size: 16px; margin-bottom: 12px; font-weight: 600;">Нужна помощь?</div>
      <div style="color: #666; margin-bottom: 20px;">
        По всем вопросам обращайтесь к нашей команде поддержки
      </div>
      <a href="mailto:support@example.com" style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: 500;">
        📧 Написать в поддержку
      </a>
    </div>
  `;
}

// Функция для показа уведомлений
function showNotification(message, type = 'info') {
  // Создаем элемент уведомления
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    animation: slideDown 0.3s ease;
  `;
  notification.textContent = message;
  
  // Добавляем стили для анимации
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideDown {
      from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
      to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(notification);
  
  // Удаляем уведомление через 3 секунды
  setTimeout(() => {
    notification.style.animation = 'slideUp 0.3s ease';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
  // По умолчанию показываем ключи и активируем вкладку 'Ключи'
  showKeys();
  updateActiveNav('keys-btn');
  // Добавляем обработчик для копирования ссылок по клику
  document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.href.includes('ss://')) {
      e.preventDefault();
      copyToClipboard(e.target.href);
    }
  });
}); 