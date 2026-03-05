/**
 * Dashboard (Health) Screen
 * Health ring, vital signs, comparison, recent alerts.
 */

import { emit } from '../event-bus.js';

let _container = null;
let _rendered = false;

export function render(container) {
  _container = container;
  if (_rendered) return;
  _rendered = true;

  // Health ring math
  const score = 87;
  const r = 44;
  const circumference = 2 * Math.PI * r;
  const dasharray = `${(score / 100) * circumference} ${circumference}`;

  // Dynamic car info based on selected vehicle
  const brandName = localStorage.getItem('llcar-brand-name') || 'Li Auto';
  const modelName = localStorage.getItem('llcar-model-name') || 'L7';
  const carLabel = `${brandName} ${modelName}`;
  const carMileage = '48 230'; // TODO: real mileage from OBD
  const carInfoText = `${carLabel} \u2022 ${carMileage} \u043A\u043C`;
  const comparisonText = `\u0421\u0440\u0435\u0434\u0438 \u0430\u043D\u0430\u043B\u043E\u0433\u0438\u0447\u043D\u044B\u0445 ${carLabel}`;

  container.innerHTML = `
    <div class="screen__scrollable" style="display:flex;flex-direction:column;gap:4px;flex:1;">
      <!-- Greeting -->
      <div style="display:flex;flex-direction:column;align-items:center;gap:4px;padding:16px 20px 0;">
        <h1 style="font-size:22px;font-weight:700;color:var(--text-primary);text-align:center;width:100%;" data-i18n="dashboard.greeting">\u0414\u043E\u0431\u0440\u044B\u0439 \u0434\u0435\u043D\u044C!</h1>
      </div>

      <!-- Spacer header -->
      <div style="height:44px;"></div>

      <!-- Car info -->
      <div style="display:flex;align-items:center;justify-content:center;width:100%;">
        <span style="font-size:13px;color:var(--text-secondary);text-align:center;" id="dashboard-car-info">${carInfoText}</span>
      </div>

      <!-- Health Score -->
      <div style="display:flex;flex-direction:column;gap:16px;padding:8px 20px;">
        <div style="display:flex;align-items:center;justify-content:center;background:var(--bg-card);border:1px solid var(--border-default);border-radius:var(--radius-lg);padding:12px;height:150px;width:100%;">
          <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
            <!-- Health ring -->
            <div class="health-ring" style="width:100px;height:100px;">
              <svg width="100" height="100" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="${r}" fill="none" stroke="#1C2333" stroke-width="6"/>
                <circle cx="50" cy="50" r="${r}" fill="none" stroke="url(#healthGrad)" stroke-width="6" stroke-linecap="round" stroke-dasharray="${dasharray}" transform="rotate(-90 50 50)"/>
                <defs>
                  <linearGradient id="healthGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#00D4AA"/>
                    <stop offset="100%" stop-color="#00A3FF"/>
                  </linearGradient>
                </defs>
              </svg>
              <div class="health-ring__value" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
                <span class="health-ring__number">${score}</span>
                <span class="health-ring__of" data-i18n="dashboard.of_100">\u0438\u0437 100</span>
              </div>
            </div>
            <!-- Status badge -->
            <div class="badge badge--healthy">
              <div class="badge__dot badge__dot--healthy"></div>
              <span data-i18n="dashboard.status_good">\u0421\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u0445\u043E\u0440\u043E\u0448\u0435\u0435</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Vital Signs -->
      <div style="display:flex;flex-direction:column;gap:10px;padding:0 20px;">
        <span style="font-size:15px;font-weight:600;color:var(--text-primary);" data-i18n="dashboard.vital_signs">\u0416\u0438\u0437\u043D\u0435\u043D\u043D\u044B\u0435 \u043F\u043E\u043A\u0430\u0437\u0430\u0442\u0435\u043B\u0438</span>
        <div style="display:flex;flex-direction:column;gap:8px;width:100%;">
          <!-- Row 1 -->
          <div style="display:flex;gap:8px;width:100%;">
            <div class="vital-card">
              <div class="vital-card__header">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/></svg>
                <span class="vital-card__label" data-i18n="dashboard.coolant">\u041E\u0445\u043B\u0430\u0436\u0434\u0435\u043D\u0438\u0435</span>
              </div>
              <span class="vital-card__value">92&deg;C</span>
              <span class="vital-card__status vital-card__status--healthy" data-i18n="dashboard.normal">\u041D\u043E\u0440\u043C\u0430</span>
            </div>
            <div class="vital-card">
              <div class="vital-card__header">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="10" x="2" y="7" rx="2" ry="2"/><line x1="22" x2="22" y1="11" y2="13"/><path d="M6 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"/><path d="m7 15 3-3 3 3"/></svg>
                <span class="vital-card__label" data-i18n="dashboard.battery">\u0410\u041A\u0411</span>
              </div>
              <span class="vital-card__value">14.2V</span>
              <span class="vital-card__status vital-card__status--healthy" data-i18n="dashboard.normal">\u041D\u043E\u0440\u043C\u0430</span>
            </div>
          </div>
          <!-- Row 2 -->
          <div style="display:flex;gap:8px;width:100%;">
            <div class="vital-card">
              <div class="vital-card__header">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--status-warning)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" x2="15" y1="22" y2="22"/><line x1="4" x2="14" y1="9" y2="9"/><path d="M14 22V4a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v18"/></svg>
                <span class="vital-card__label">STFT</span>
              </div>
              <span class="vital-card__value vital-card__value--warning">+8.2%</span>
              <span class="vital-card__status vital-card__status--warning" data-i18n="dashboard.attention">\u0412\u043D\u0438\u043C\u0430\u043D\u0438\u0435</span>
            </div>
            <div class="vital-card">
              <div class="vital-card__header">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>
                <span class="vital-card__label" data-i18n="dashboard.o2_sensor">O\u2082 \u0434\u0430\u0442\u0447\u0438\u043A</span>
              </div>
              <span class="vital-card__value">0.45V</span>
              <span class="vital-card__status vital-card__status--healthy" data-i18n="dashboard.normal">\u041D\u043E\u0440\u043C\u0430</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Comparison bar -->
      <div style="padding:10px 20px;">
        <div style="display:flex;flex-direction:column;gap:4px;background:var(--bg-card);border:1px solid var(--border-default);border-radius:var(--radius-md);padding:8px 16px;height:60px;justify-content:center;width:100%;">
          <div style="display:flex;align-items:center;gap:8px;width:100%;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M7 16h8"/><path d="M7 11h12"/><path d="M7 6h3"/></svg>
            <span style="font-size:13px;font-weight:500;color:var(--text-primary);" id="dashboard-comparison">${comparisonText}</span>
          </div>
          <div style="width:100%;height:6px;background:#1C2333;border-radius:3px;overflow:hidden;">
            <div class="gradient-primary" style="height:100%;width:72%;border-radius:3px;"></div>
          </div>
          <span style="font-size:11px;color:var(--accent-primary);" data-i18n="dashboard.better_than">\u041B\u0443\u0447\u0448\u0435 72% \u0430\u043D\u0430\u043B\u043E\u0433\u0438\u0447\u043D\u044B\u0445 \u0430\u0432\u0442\u043E</span>
        </div>
      </div>

      <!-- Quick Actions -->
      <div style="display:flex;gap:8px;padding:4px 20px;">
        <button class="btn" id="btn-open-cert" style="flex:1;background:var(--bg-card);border:1px solid var(--border-accent);border-radius:var(--radius-md);padding:10px;display:flex;align-items:center;justify-content:center;gap:8px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 15l2 2 4-4"/></svg>
          <span style="font-size:12px;font-weight:600;color:var(--accent-primary);" data-i18n="dashboard.health_cert">\u041C\u0435\u0434. \u043A\u0430\u0440\u0442\u0430</span>
        </button>
        <button class="btn" id="btn-change-car" style="flex:1;background:var(--bg-card);border:1px solid var(--border-default);border-radius:var(--radius-md);padding:10px;display:flex;align-items:center;justify-content:center;gap:8px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>
          <span style="font-size:12px;font-weight:600;color:var(--text-secondary);" data-i18n="dashboard.change_car">\u0421\u043C\u0435\u043D\u0438\u0442\u044C \u0430\u0432\u0442\u043E</span>
        </button>
      </div>

      <!-- Recent Alerts -->
      <div style="display:flex;flex-direction:column;gap:10px;padding:4px 20px 8px;flex:1;">
        <span style="font-size:15px;font-weight:600;color:var(--text-primary);" data-i18n="dashboard.recent_alerts">\u041F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435 \u043E\u043F\u043E\u0432\u0435\u0449\u0435\u043D\u0438\u044F</span>

        <div class="alert-item">
          <div class="alert-item__icon alert-item__icon--warning">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--status-warning)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
          </div>
          <div class="alert-item__content">
            <span class="alert-item__title" data-i18n="dashboard.alert_fuel">\u041A\u043E\u0440\u0440\u0435\u043A\u0446\u0438\u044F \u0442\u043E\u043F\u043B\u0438\u0432\u0430 \u0432\u044B\u0448\u0435 \u043D\u043E\u0440\u043C\u044B</span>
            <span class="alert-item__subtitle">STFT +8.2% &bull; <span data-i18n="dashboard.alert_fuel_sub">\u0420\u0435\u043A\u043E\u043C\u0435\u043D\u0434\u0443\u0435\u043C \u043F\u0440\u043E\u0432\u0435\u0440\u0438\u0442\u044C</span></span>
          </div>
        </div>

        <div class="alert-item">
          <div class="alert-item__icon alert-item__icon--healthy">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--status-healthy)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
          </div>
          <div class="alert-item__content">
            <span class="alert-item__title" data-i18n="dashboard.alert_oil">\u041C\u0430\u0441\u043B\u043E \u0437\u0430\u043C\u0435\u043D\u0435\u043D\u043E \u0443\u0441\u043F\u0435\u0448\u043D\u043E</span>
            <span class="alert-item__subtitle" data-i18n="dashboard.alert_oil_sub">\u0421\u043B\u0435\u0434\u0443\u044E\u0449\u0430\u044F \u0437\u0430\u043C\u0435\u043D\u0430 \u0447\u0435\u0440\u0435\u0437 8 500 \u043A\u043C</span>
          </div>
        </div>
      </div>
    </div>
  `;

  bindEvents();
}

function bindEvents() {
  const certBtn = _container.querySelector('#btn-open-cert');
  if (certBtn) {
    certBtn.addEventListener('click', () => {
      emit('app:navigate', { screen: 'certificate' });
    });
  }

  const carBtn = _container.querySelector('#btn-change-car');
  if (carBtn) {
    carBtn.addEventListener('click', () => {
      emit('app:navigate', { screen: 'onboarding' });
    });
  }
}

export function cleanup() {
  _rendered = false;
  if (_container) {
    _container.innerHTML = '';
  }
}
