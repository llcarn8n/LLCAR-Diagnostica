/**
 * Diagnostics Screen
 * DTC error codes, severity, probable causes, recommendations.
 */

import { emit } from '../event-bus.js';

let _container = null;
let _rendered = false;

export function render(container) {
  _container = container;
  if (_rendered) return;
  _rendered = true;

  // Severity ring math
  const severity = 5;
  const r = 24;
  const circumference = 2 * Math.PI * r;
  const dasharray = `${(severity / 10) * circumference} ${circumference}`;

  container.innerHTML = `
    <div class="screen__scrollable" style="display:flex;flex-direction:column;gap:6px;flex:1;">
      <!-- Header -->
      <div style="display:flex;align-items:center;gap:12px;height:36px;padding:0 20px;">
        <button id="diag-back" style="background:none;border:none;cursor:pointer;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--text-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <span style="font-size:17px;font-weight:600;color:var(--text-primary);" data-i18n="diag.title">\u0420\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u044B \u0430\u043D\u0430\u043B\u0438\u0437\u043E\u0432</span>
      </div>

      <!-- Report meta -->
      <div style="display:flex;align-items:center;justify-content:space-between;padding:0 20px;">
        <span style="font-size:12px;color:var(--text-tertiary);">26 <span data-i18n="diag.feb">\u0444\u0435\u0432</span> 2026 &bull; 48 230 <span data-i18n="diag.km">\u043A\u043C</span></span>
        <div style="display:flex;align-items:center;gap:4px;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          <span style="font-size:12px;font-weight:500;color:var(--accent-primary);">PDF</span>
        </div>
      </div>

      <!-- Can I Drive Card -->
      <div style="padding:8px 20px;">
        <div style="display:flex;align-items:center;gap:10px;background:var(--status-warning-dim);border:1px solid rgba(210,153,34,0.25);border-radius:var(--radius-lg);padding:16px;">
          <div style="width:48px;height:48px;border-radius:24px;background:var(--status-warning);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--text-on-accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>
          </div>
          <div style="display:flex;flex-direction:column;gap:4px;flex:1;min-width:0;">
            <span style="font-size:11px;font-weight:500;color:var(--status-warning);" data-i18n="diag.can_drive">\u041C\u043E\u0436\u043D\u043E \u043B\u0438 \u0435\u0445\u0430\u0442\u044C?</span>
            <span style="font-size:16px;font-weight:700;color:var(--text-primary);" data-i18n="diag.drive_answer">\u0414\u0430, \u043D\u043E \u0441 \u043E\u0433\u0440\u0430\u043D\u0438\u0447\u0435\u043D\u0438\u044F\u043C\u0438</span>
            <span style="font-size:11px;color:var(--text-secondary);" data-i18n="diag.drive_hint">\u0421\u0422\u041E \u0437\u0430 2 \u043D\u0435\u0434\u0435\u043B\u0438</span>
          </div>
        </div>
      </div>

      <!-- DTC Error -->
      <div style="display:flex;flex-direction:column;gap:12px;padding:6px 20px;">
        <div class="card" style="display:flex;flex-direction:column;gap:10px;">
          <!-- Top row with severity ring -->
          <div style="display:flex;align-items:center;gap:14px;">
            <div class="severity-ring">
              <svg width="56" height="56" viewBox="0 0 56 56">
                <circle cx="28" cy="28" r="${r}" fill="none" stroke="#1C2333" stroke-width="4"/>
                <circle cx="28" cy="28" r="${r}" fill="none" stroke="#D29922" stroke-width="4" stroke-linecap="round" stroke-dasharray="${dasharray}" transform="rotate(-90 28 28)"/>
              </svg>
              <div class="severity-ring__value">
                <span class="severity-ring__number" style="color:var(--status-warning);">${severity}</span>
                <span class="severity-ring__total">/10</span>
              </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:4px;flex:1;min-width:0;">
              <span class="chip chip--warning" style="align-self:flex-start;font-size:13px;font-weight:700;letter-spacing:1px;padding:3px 8px;">P0171</span>
              <span style="font-size:12px;font-weight:500;color:var(--text-primary);" data-i18n="diag.fuel_mixture">\u0422\u043E\u043F\u043B\u0438\u0432\u043D\u0430\u044F \u0441\u043C\u0435\u0441\u044C &middot; \u0411\u0430\u043D\u043A 1</span>
            </div>
          </div>

          <!-- Cause probabilities -->
          <div class="cause-item">
            <span class="cause-item__pct">45%</span>
            <span class="cause-item__label" data-i18n="diag.cause_air_leak">\u041F\u043E\u0434\u0441\u043E\u0441 \u0432\u043E\u0437\u0434\u0443\u0445\u0430</span>
          </div>
          <div class="cause-item">
            <span class="cause-item__pct">30%</span>
            <span class="cause-item__label" data-i18n="diag.cause_maf">\u0414\u0430\u0442\u0447\u0438\u043A MAF</span>
          </div>
          <div class="cause-item">
            <span class="cause-item__pct">15%</span>
            <span class="cause-item__label" data-i18n="diag.cause_fuel_pressure">\u0414\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u0442\u043E\u043F\u043B\u0438\u0432\u0430</span>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div style="padding:6px 20px;">
        <div style="display:flex;align-items:center;justify-content:space-between;background:var(--bg-card);border:1px solid var(--border-default);border-radius:var(--radius-md);padding:12px 14px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/></svg>
            <span style="font-size:13px;font-weight:600;color:var(--text-primary);" data-i18n="diag.recommendations">\u0420\u0435\u043A\u043E\u043C\u0435\u043D\u0434\u0430\u0446\u0438\u0438 \u0432\u0440\u0430\u0447\u0430</span>
          </div>
          <div style="display:flex;align-items:center;gap:6px;">
            <span style="font-size:12px;font-weight:600;color:var(--accent-primary);">3</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
          </div>
        </div>
      </div>

      <!-- Analysis Summary -->
      <div style="display:flex;flex-direction:column;gap:8px;padding:6px 16px;">
        <div style="display:flex;align-items:center;gap:6px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></svg>
          <span style="font-size:13px;font-weight:600;color:var(--text-primary);" data-i18n="diag.summary">\u0421\u0432\u043E\u0434\u043A\u0430 \u0430\u043D\u0430\u043B\u0438\u0437\u0430</span>
        </div>

        <!-- Summary cards row -->
        <div style="display:flex;gap:8px;width:100%;">
          <div class="summary-card" style="background:var(--bg-card);border-color:var(--border-default);">
            <span class="summary-card__value" style="color:var(--accent-primary);">87</span>
            <span class="summary-card__label" style="color:var(--accent-primary);" data-i18n="diag.total_score">\u041E\u0431\u0449\u0438\u0439 \u0431\u0430\u043B\u043B</span>
          </div>
          <div class="summary-card" style="background:rgba(63,185,80,0.06);border-color:rgba(63,185,80,0.19);">
            <span class="summary-card__value" style="color:var(--status-healthy);">12</span>
            <span class="summary-card__label" style="color:var(--status-healthy);" data-i18n="diag.normal">\u0412 \u043D\u043E\u0440\u043C\u0435</span>
          </div>
          <div class="summary-card" style="background:rgba(248,81,73,0.06);border-color:rgba(248,81,73,0.19);">
            <span class="summary-card__value" style="color:var(--status-critical);">3</span>
            <span class="summary-card__label" style="color:var(--status-critical);" data-i18n="diag.deviations">\u041E\u0442\u043A\u043B\u043E\u043D\u0435\u043D\u0438\u044F</span>
          </div>
        </div>

        <div style="width:100%;height:1px;background:var(--bg-surface);"></div>

        <!-- Problems -->
        <div style="display:flex;align-items:center;gap:6px;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--status-warning)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
          <span style="font-size:12px;font-weight:600;color:var(--text-primary);" data-i18n="diag.need_attention">\u0422\u0440\u0435\u0431\u0443\u044E\u0442 \u0432\u043D\u0438\u043C\u0430\u043D\u0438\u044F</span>
        </div>

        <div class="problem-item" style="border-color:rgba(210,153,34,0.19);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--status-warning)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>
          <div class="problem-item__content">
            <span class="problem-item__title" data-i18n="diag.o2_voltage">\u041D\u0430\u043F\u0440\u044F\u0436\u0435\u043D\u0438\u0435 O2</span>
            <span class="problem-item__desc" style="color:var(--status-warning);">0.45V &bull; <span data-i18n="diag.o2_norm">\u043D\u043E\u0440\u043C\u0430 0.1&ndash;0.9V</span></span>
          </div>
        </div>

        <div class="problem-item" style="border-color:rgba(248,81,73,0.19);">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--status-critical)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/></svg>
          <div class="problem-item__content">
            <span class="problem-item__title" data-i18n="diag.fuel_pressure">\u0414\u0430\u0432\u043B\u0435\u043D\u0438\u0435 \u0442\u043E\u043F\u043B\u0438\u0432\u0430</span>
            <span class="problem-item__desc" style="color:var(--status-critical);">280 <span data-i18n="diag.kpa">\u043A\u041F\u0430</span> &bull; <span data-i18n="diag.fuel_norm">\u043D\u043E\u0440\u043C\u0430 350&ndash;400 \u043A\u041F\u0430</span></span>
          </div>
        </div>
      </div>

      <!-- Ask Doctor Button -->
      <div style="padding:6px 20px;">
        <button class="btn btn--primary" id="btn-ask-doctor" style="height:48px;font-size:14px;font-weight:600;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>
          <span data-i18n="diag.ask_doctor">\u0421\u043F\u0440\u043E\u0441\u0438\u0442\u044C \u0434\u043E\u043A\u0442\u043E\u0440\u0430</span>
        </button>
      </div>
    </div>
  `;

  bindEvents();
}

function bindEvents() {
  const backBtn = _container.querySelector('#diag-back');
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      emit('app:navigate', { screen: 'dashboard' });
    });
  }

  const askDoctorBtn = _container.querySelector('#btn-ask-doctor');
  if (askDoctorBtn) {
    askDoctorBtn.addEventListener('click', () => {
      emit('app:navigate', { screen: 'doctor' });
    });
  }
}

export function cleanup() {
  _rendered = false;
  if (_container) {
    _container.innerHTML = '';
  }
}
