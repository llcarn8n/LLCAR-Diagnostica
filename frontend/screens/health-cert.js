/**
 * Health Certificate Screen
 * Car name, health ring, health trend chart, systems breakdown, QR code, actions.
 */

import { emit } from '../event-bus.js';

let _container = null;
let _rendered = false;

export function render(container) {
  _container = container;
  if (_rendered) return;
  _rendered = true;

  // Health ring math (smaller version)
  const score = 87;
  const r = 35;
  const circumference = 2 * Math.PI * r;
  const dasharray = `${(score / 100) * circumference} ${circumference}`;

  container.innerHTML = `
    <div class="screen__scrollable" style="display:flex;flex-direction:column;gap:12px;flex:1;">
      <!-- Header -->
      <div style="display:flex;align-items:center;gap:12px;height:44px;padding:0 20px;">
        <button id="cert-back" style="background:none;border:none;cursor:pointer;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--text-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <span style="font-size:17px;font-weight:600;color:var(--text-primary);" data-i18n="cert.title">\u041C\u0435\u0434\u0438\u0446\u0438\u043D\u0441\u043A\u0430\u044F \u043A\u0430\u0440\u0442\u0430</span>
      </div>

      <!-- Certificate card -->
      <div style="padding:4px 20px 0;">
        <div style="display:flex;flex-direction:column;align-items:center;gap:6px;background:var(--bg-card);border:1px solid var(--border-accent);border-radius:var(--radius-xl);padding:10px;width:100%;">
          <span style="font-size:14px;font-weight:700;color:var(--text-primary);">Li Auto L7</span>

          <!-- Health ring -->
          <div class="health-ring" style="width:80px;height:80px;">
            <svg width="80" height="80" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="${r}" fill="none" stroke="#1C2333" stroke-width="5"/>
              <circle cx="40" cy="40" r="${r}" fill="none" stroke="url(#certGrad)" stroke-width="5" stroke-linecap="round" stroke-dasharray="${dasharray}" transform="rotate(-90 40 40)"/>
              <defs>
                <linearGradient id="certGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#00D4AA"/>
                  <stop offset="100%" stop-color="#00A3FF"/>
                </linearGradient>
              </defs>
            </svg>
            <div class="health-ring__value" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
              <span class="health-ring__number health-ring__number--medium">${score}</span>
              <span class="health-ring__of health-ring__of--small" data-i18n="cert.of_100">\u0438\u0437 100</span>
            </div>
          </div>

          <!-- Status badge -->
          <div class="badge badge--healthy">
            <span style="font-weight:600;" data-i18n="cert.status_good">\u0421\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u0445\u043E\u0440\u043E\u0448\u0435\u0435</span>
          </div>
        </div>

        <!-- Health Trend Chart -->
        <div style="display:flex;flex-direction:column;gap:8px;background:var(--bg-card);border:1px solid var(--border-default);border-radius:var(--radius-md);padding:12px 14px;width:100%;margin-top:8px;">
          <div style="display:flex;align-items:center;justify-content:space-between;width:100%;">
            <span style="font-size:12px;font-weight:600;color:var(--text-primary);" data-i18n="cert.health_trend">\u0414\u0438\u043D\u0430\u043C\u0438\u043A\u0430 \u0437\u0434\u043E\u0440\u043E\u0432\u044C\u044F</span>
            <span class="chip chip--healthy" style="font-size:10px;font-weight:600;">&#9650; +9 <span data-i18n="cert.in_6mo">\u0437\u0430 6 \u043C\u0435\u0441</span></span>
          </div>

          <!-- Chart with 3 paths -->
          <div class="trend-gradient" style="position:relative;width:100%;height:44px;border-radius:6px;overflow:hidden;">
            <svg width="100%" height="100%" viewBox="0 0 322 44" preserveAspectRatio="none" fill="none">
              <path d="M0,32 C20,28 40,20 60,22 C80,24 100,16 120,14 C140,12 160,18 180,12 C200,6 220,10 240,6 C260,2 280,8 300,4 L322,2" stroke="#00D4AA" stroke-width="2" fill="none"/>
              <circle cx="318" cy="2" r="4" fill="#00D4AA"/>
              <path d="M0,20 C20,24 40,28 60,22 C80,16 100,24 120,20 C140,16 160,22 180,18 C200,14 220,20 240,16 C260,12 280,18 300,16 L322,17" stroke="#00A3FF" stroke-width="2" fill="none"/>
              <circle cx="319" cy="17" r="3" fill="#00A3FF"/>
              <path d="M0,12 C20,16 40,14 60,18 C80,22 100,20 120,24 C140,28 160,24 180,28 C200,32 220,28 240,32 C260,36 280,30 300,33 L322,33" stroke="#D29922" stroke-width="2" fill="none"/>
              <circle cx="319" cy="33" r="3" fill="#D29922"/>
            </svg>
          </div>

          <div style="display:flex;align-items:center;justify-content:space-between;width:100%;">
            <span style="font-size:10px;color:var(--text-tertiary);"><span data-i18n="cert.sep">\u0421\u0435\u043D</span> &middot; 78</span>
            <span style="font-size:10px;font-weight:600;color:var(--accent-primary);"><span data-i18n="cert.feb">\u0424\u0435\u0432</span> &middot; 87</span>
          </div>
        </div>
      </div>

      <!-- Systems Breakdown -->
      <div style="display:flex;flex-direction:column;gap:6px;padding:4px 20px 0;">
        <span style="font-size:15px;font-weight:600;color:var(--text-primary);" data-i18n="cert.systems">\u0421\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u0441\u0438\u0441\u0442\u0435\u043C</span>
        <div style="display:flex;flex-direction:column;gap:8px;">
          <!-- Row 1 -->
          <div style="display:flex;gap:8px;">
            ${systemCard('\u041A\u0443\u0437\u043E\u0432', 95, 'healthy')}
            ${systemCard('\u0414\u0432\u0438\u0433\u0430\u0442\u0435\u043B\u044C', 82, 'healthy')}
            ${systemCard('\u041F\u0440\u0438\u0432\u043E\u0434', 88, 'healthy')}
            ${systemCard('\u042D\u043B\u0435\u043A\u0442\u0440\u043E', 91, 'healthy')}
          </div>
          <!-- Row 2 -->
          <div style="display:flex;gap:8px;">
            ${systemCard('\u0423\u043F\u0440\u0430\u0432\u043B.', 74, 'warning')}
            ${systemCard('\u0414\u0430\u0442\u0447\u0438\u043A\u0438', 96, 'healthy')}
            ${systemCard('\u041A\u043B\u0438\u043C\u0430\u0442', 89, 'healthy')}
            ${systemCard('\u042D\u043B\u0435\u043A\u0442\u0440\u043E\u043D.', 93, 'healthy')}
          </div>
        </div>
      </div>

      <!-- Info Row -->
      <div style="display:flex;align-items:center;gap:12px;padding:4px 20px 0;">
        <div style="width:44px;height:44px;border-radius:6px;background:white;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--text-on-accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="5" height="5" x="3" y="3" rx="1"/><rect width="5" height="5" x="16" y="3" rx="1"/><rect width="5" height="5" x="3" y="16" rx="1"/><rect width="5" height="5" x="16" y="16" rx="1"/><path d="M21 16h-3a2 2 0 0 0-2 2v3"/><path d="M21 21v.01"/><path d="M12 7v3a2 2 0 0 1-2 2H7"/><path d="M3 12h.01"/><path d="M12 3h.01"/><path d="M12 16v.01"/><path d="M16 12h1"/><path d="M21 12v.01"/><path d="M12 21v-1"/></svg>
        </div>
        <div style="display:flex;flex-direction:column;gap:2px;flex:1;min-width:0;">
          <span style="font-size:12px;font-weight:600;color:var(--text-primary);">#LLCAR-2026-0847</span>
          <span style="font-size:10px;color:var(--text-tertiary);">26 <span data-i18n="cert.february">\u0444\u0435\u0432\u0440\u0430\u043B\u044F</span> 2026 &middot; 42 380 <span data-i18n="cert.km">\u043A\u043C</span></span>
          <span style="font-size:10px;color:var(--accent-primary);" data-i18n="cert.valid_until">\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0442\u0435\u043B\u0435\u043D \u0434\u043E 26.08.2026</span>
        </div>
      </div>

      <!-- Actions -->
      <div style="display:flex;gap:8px;padding:4px 20px;">
        <button class="btn" style="flex:1;background:var(--accent-primary);border-radius:var(--radius-md);padding:12px;color:var(--text-on-accent);font-size:14px;font-weight:600;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
          <span data-i18n="cert.share">\u041F\u043E\u0434\u0435\u043B\u0438\u0442\u044C\u0441\u044F</span>
        </button>
        <button class="btn btn--secondary" style="flex:1;font-size:14px;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          <span data-i18n="cert.download_pdf">\u0421\u043A\u0430\u0447\u0430\u0442\u044C PDF</span>
        </button>
      </div>
    </div>
  `;

  bindEvents();
}

function systemCard(label, score, status) {
  const color = status === 'warning' ? 'var(--status-warning)' : 'var(--status-healthy)';
  return `
    <div class="system-card">
      <span class="system-card__score" style="color:${color};">${score}</span>
      <span class="system-card__label">${label}</span>
    </div>
  `;
}

function bindEvents() {
  const backBtn = _container.querySelector('#cert-back');
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      emit('app:navigate', { screen: 'dashboard' });
    });
  }
}

export function cleanup() {
  _rendered = false;
  if (_container) {
    _container.innerHTML = '';
  }
}
