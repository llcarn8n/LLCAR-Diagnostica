/**
 * AI Assistant (Doctor) Screen
 * Chat interface with bot messages, user messages, data card, suggested chips.
 */

import { emit } from '../event-bus.js';

let _container = null;
let _rendered = false;

export function render(container) {
  _container = container;
  if (_rendered) return;
  _rendered = true;

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;flex:1;overflow:hidden;">
      <!-- Header -->
      <div style="display:flex;align-items:center;gap:10px;height:48px;padding:0 20px;">
        <div class="gradient-primary" style="width:32px;height:32px;border-radius:16px;display:flex;align-items:center;justify-content:center;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--text-on-accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
        </div>
        <span style="font-size:17px;font-weight:600;color:var(--text-primary);" data-i18n="doctor.title">\u0414\u043E\u043A\u0442\u043E\u0440 \u043D\u0430 \u0441\u0432\u044F\u0437\u0438</span>
        <span class="chip chip--accent" style="border-radius:10px;">AI</span>
      </div>

      <!-- Chat Area -->
      <div class="chat-area">
        <!-- Bot Message 1 -->
        <div class="chat-msg chat-msg--bot">
          <div class="chat-msg__avatar">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
          </div>
          <div class="chat-msg__bubble chat-msg__bubble--bot">
            <p class="chat-msg__text" data-i18n="doctor.msg_hello">\u0417\u0434\u0440\u0430\u0432\u0441\u0442\u0432\u0443\u0439\u0442\u0435! \u042F \u0432\u0430\u0448 \u0430\u0432\u0442\u043E\u043C\u043E\u0431\u0438\u043B\u044C\u043D\u044B\u0439 \u0434\u043E\u043A\u0442\u043E\u0440. \u0412\u0438\u0436\u0443, \u0447\u0442\u043E \u043A\u043E\u0440\u0440\u0435\u043A\u0446\u0438\u044F \u0442\u043E\u043F\u043B\u0438\u0432\u0430 \u043D\u0435\u043C\u043D\u043E\u0433\u043E \u043F\u043E\u0432\u044B\u0448\u0435\u043D\u0430. \u0414\u0430\u0432\u0430\u0439\u0442\u0435 \u0440\u0430\u0437\u0431\u0435\u0440\u0451\u043C\u0441\u044F.</p>
            <span class="chat-msg__time">9:38</span>
          </div>
        </div>

        <!-- Data Card (STFT Chart) -->
        <div class="chat-data-card">
          <div class="chat-data-card__header">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/></svg>
            <span class="chat-data-card__title" data-i18n="doctor.stft_week">\u041F\u043E\u043A\u0430\u0437\u0430\u043D\u0438\u044F STFT \u0437\u0430 \u043D\u0435\u0434\u0435\u043B\u044E</span>
          </div>
          <div class="chat-data-card__chart">
            <svg viewBox="0 0 240 60" preserveAspectRatio="none">
              <line x1="8" y1="16" x2="248" y2="16" stroke="#D29922" stroke-width="1" stroke-dasharray="4 4"/>
              <polyline points="8,45 30,42 55,40 80,38 105,35 130,30 155,28 180,25 205,20 230,15 248,12" fill="none" stroke="#00D4AA" stroke-width="2"/>
            </svg>
          </div>
          <div class="chat-data-card__footer">
            <span style="font-size:10px;color:var(--status-healthy);" data-i18n="doctor.stft_min">\u041C\u0438\u043D: +3.1%</span>
            <span style="font-size:10px;color:var(--status-warning);" data-i18n="doctor.stft_max">\u041C\u0430\u043A\u0441: +8.2%</span>
            <span style="font-size:10px;color:var(--text-tertiary);" data-i18n="doctor.stft_norm">\u041D\u043E\u0440\u043C\u0430: &plusmn;5%</span>
          </div>
        </div>

        <!-- User Message -->
        <div class="chat-msg chat-msg--user">
          <div class="chat-msg__bubble chat-msg__bubble--user">
            <p class="chat-msg__text" data-i18n="doctor.msg_user_q">\u0427\u0442\u043E \u0437\u043D\u0430\u0447\u0438\u0442 P0171? \u041D\u0430\u0441\u043A\u043E\u043B\u044C\u043A\u043E \u044D\u0442\u043E \u0441\u0435\u0440\u044C\u0451\u0437\u043D\u043E?</p>
            <span class="chat-msg__time">9:39</span>
          </div>
        </div>

        <!-- Bot Message 2 -->
        <div class="chat-msg chat-msg--bot">
          <div class="chat-msg__avatar">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
          </div>
          <div class="chat-msg__bubble chat-msg__bubble--bot">
            <p class="chat-msg__text" data-i18n="doctor.msg_answer">P0171 &mdash; \u043E\u0431\u0435\u0434\u043D\u0451\u043D\u043D\u0430\u044F \u0442\u043E\u043F\u043B\u0438\u0432\u043D\u0430\u044F \u0441\u043C\u0435\u0441\u044C. \u0412\u0430\u0448 \u0434\u0432\u0438\u0433\u0430\u0442\u0435\u043B\u044C \u043F\u043E\u043B\u0443\u0447\u0430\u0435\u0442 \u0441\u043B\u0438\u0448\u043A\u043E\u043C \u043C\u0430\u043B\u043E \u0442\u043E\u043F\u043B\u0438\u0432\u0430. \u0421\u0435\u0440\u044C\u0451\u0437\u043D\u043E\u0441\u0442\u044C: 5/10. \u0415\u0445\u0430\u0442\u044C \u043C\u043E\u0436\u043D\u043E, \u043D\u043E \u0437\u0430\u043F\u043B\u0430\u043D\u0438\u0440\u0443\u0439\u0442\u0435 \u0432\u0438\u0437\u0438\u0442.</p>
            <span class="chat-msg__time">9:40</span>
          </div>
        </div>

        <!-- Suggested chips -->
        <div class="chat-chips">
          <button class="chat-chip" data-i18n="doctor.chip_causes">\u0412\u0435\u0440\u043E\u044F\u0442\u043D\u044B\u0435 \u043F\u0440\u0438\u0447\u0438\u043D\u044B?</button>
          <button class="chat-chip" data-i18n="doctor.chip_cost">\u0421\u043A\u043E\u043B\u044C\u043A\u043E \u0441\u0442\u043E\u0438\u0442?</button>
        </div>
      </div>

      <!-- Input Bar -->
      <div class="chat-input-bar">
        <div class="chat-input-bar__field">
          <input type="text" id="chat-input" placeholder="\u0421\u043F\u0440\u043E\u0441\u0438\u0442\u0435 \u0434\u043E\u043A\u0442\u043E\u0440\u0430..." data-i18n-placeholder="doctor.input_placeholder">
        </div>
        <button class="chat-input-bar__send" id="chat-send">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-on-accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
        </button>
      </div>
    </div>
  `;

  bindEvents();
}

function bindEvents() {
  const sendBtn = _container.querySelector('#chat-send');
  const input = _container.querySelector('#chat-input');

  if (sendBtn && input) {
    const doSend = () => {
      const text = input.value.trim();
      if (!text) return;
      emit('doctor:send', { text });
      input.value = '';
    };

    sendBtn.addEventListener('click', doSend);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') doSend();
    });
  }

  // Suggested chips
  _container.querySelectorAll('.chat-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const text = chip.textContent.trim();
      emit('doctor:send', { text });
    });
  });
}

export function cleanup() {
  _rendered = false;
  if (_container) {
    _container.innerHTML = '';
  }
}
