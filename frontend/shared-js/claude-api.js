// ══════════════════════════════════════════════════════════
// Claude API модуль — извлечён из find-3d.html
// Единый интерфейс доступа к Anthropic Claude API
// ══════════════════════════════════════════════════════════

const STORAGE_KEY = 'llcar_claude_api_key';
const API_URL = 'https://api.anthropic.com/v1/messages';
const ANTHROPIC_VERSION = '2023-06-01';

/**
 * Ошибка Claude API с расширенной информацией
 */
export class ClaudeAPIError extends Error {
    /**
     * @param {string} message
     * @param {string} code - 'RATE_LIMIT' | 'AUTH_ERROR' | 'NETWORK_ERROR' | 'OVERLOADED' | 'UNKNOWN'
     * @param {number} status - HTTP статус
     * @param {number} [retryAfter] - Секунд до повтора
     */
    constructor(message, code, status, retryAfter) {
        super(message);
        this.name = 'ClaudeAPIError';
        this.code = code;
        this.status = status;
        this.retryAfter = retryAfter;
    }
}

/**
 * Класс для работы с Claude API
 */
export class ClaudeAPI {
    /**
     * @param {string} apiKey - API ключ Anthropic
     * @param {Object} options
     * @param {string} [options.model='claude-sonnet-4-5-20250929'] - ID модели Claude
     * @param {number} [options.maxTokens=4096] - Максимум токенов в ответе
     * @param {string} [options.systemPrompt=''] - Системный промпт для контекста
     * @param {string} [options.language='ru'] - Язык ответов
     */
    constructor(apiKey, options = {}) {
        this._apiKey = apiKey || '';
        this._model = options.model || 'claude-sonnet-4-5-20250929';
        this._maxTokens = options.maxTokens || 4096;
        this._systemPrompt = options.systemPrompt || '';
        this._language = options.language || 'ru';
        this._stats = { requestCount: 0, totalTokens: 0, errors: 0 };
    }

    /**
     * Отправить запрос к Claude API
     * @param {Array} messages - Массив сообщений [{role, content}]
     * @param {Object} [overrides] - Переопределения параметров
     * @returns {Promise<{text: string, usage: Object, stopReason: string}>}
     */
    async _request(messages, overrides = {}) {
        const apiKey = this._apiKey;
        if (!apiKey) {
            throw new ClaudeAPIError('API ключ не задан', 'AUTH_ERROR', 0);
        }

        const body = {
            model: overrides.model || this._model,
            max_tokens: overrides.maxTokens || this._maxTokens,
            messages
        };

        if (this._systemPrompt || overrides.systemPrompt) {
            body.system = overrides.systemPrompt || this._systemPrompt;
        }

        this._stats.requestCount++;

        let resp;
        try {
            resp = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': apiKey,
                    'anthropic-version': ANTHROPIC_VERSION,
                    'anthropic-dangerous-direct-browser-access': 'true'
                },
                body: JSON.stringify(body)
            });
        } catch (e) {
            this._stats.errors++;
            throw new ClaudeAPIError(
                'Ошибка сети: ' + e.message,
                'NETWORK_ERROR',
                0
            );
        }

        if (!resp.ok) {
            this._stats.errors++;
            const errData = await resp.json().catch(() => ({}));
            const msg = errData.error?.message || `HTTP ${resp.status}`;
            let code = 'UNKNOWN';
            let retryAfter;

            if (resp.status === 401) code = 'AUTH_ERROR';
            else if (resp.status === 429) {
                code = 'RATE_LIMIT';
                retryAfter = parseInt(resp.headers.get('retry-after')) || 60;
            }
            else if (resp.status === 529) code = 'OVERLOADED';

            throw new ClaudeAPIError(msg, code, resp.status, retryAfter);
        }

        const data = await resp.json();
        const text = data.content?.[0]?.text || '';
        const usage = data.usage || {};
        this._stats.totalTokens += (usage.input_tokens || 0) + (usage.output_tokens || 0);

        return { text, usage, stopReason: data.stop_reason };
    }

    /**
     * Отправить вопрос в Claude API
     * @param {string} prompt - Вопрос пользователя
     * @param {Object|null} context - Дополнительный контекст
     * @returns {Promise<string>} Текстовый ответ
     */
    async ask(prompt, context = null) {
        let fullPrompt = prompt;
        if (context) {
            const parts = [];
            if (context.vehicleModel) parts.push(`Автомобиль: Li Auto ${context.vehicleModel}`);
            if (context.componentName) parts.push(`Компонент: ${context.componentName}`);
            if (context.dtcCode) parts.push(`DTC-код: ${context.dtcCode}`);
            if (context.manualExcerpt) parts.push(`Из мануала:\n${context.manualExcerpt}`);
            if (parts.length > 0) {
                fullPrompt = `Контекст:\n${parts.join('\n')}\n\nВопрос: ${prompt}`;
            }
        }

        const systemPrompt = this._systemPrompt ||
            `Ты автомобильный диагност для Li Auto. Отвечай кратко и по делу на русском языке. Если не уверен в ответе — скажи об этом.`;

        const { text } = await this._request(
            [{ role: 'user', content: fullPrompt }],
            { systemPrompt }
        );
        return text;
    }

    /**
     * Перевести текст
     * @param {string} text - Исходный текст
     * @param {string} fromLang - Исходный язык ('zh', 'en', 'ru')
     * @param {string} toLang - Целевой язык ('zh', 'en', 'ru')
     * @returns {Promise<string>} Переведённый текст
     */
    async translate(text, fromLang, toLang) {
        const langNames = { zh: 'китайского', en: 'английского', ru: 'русского' };
        const langNamesTo = { zh: 'китайский', en: 'английский', ru: 'русский' };
        const prompt = `Переведи следующий текст с ${langNames[fromLang] || fromLang} на ${langNamesTo[toLang] || toLang}. Верни ТОЛЬКО перевод, без пояснений.\n\nТекст:\n${text}`;

        const { text: translated } = await this._request(
            [{ role: 'user', content: prompt }],
            { systemPrompt: 'Ты профессиональный переводчик. Переводи точно, сохраняя смысл и технические термины.' }
        );
        return translated;
    }

    /**
     * Анализ DTC-кода через Claude
     * @param {string} code - DTC-код (например 'P0300')
     * @param {Object} vehicleContext
     * @returns {Promise<Object>} Структурированный ответ DtcAnalysis
     */
    async analyzeDTC(code, vehicleContext = {}) {
        const parts = [`Проанализируй DTC-код: ${code}`];
        if (vehicleContext.vehicle) parts.push(`Автомобиль: ${vehicleContext.vehicle}`);
        if (vehicleContext.symptoms) parts.push(`Симптомы: ${vehicleContext.symptoms}`);
        if (vehicleContext.relatedCodes?.length) {
            parts.push(`Сопутствующие коды: ${vehicleContext.relatedCodes.join(', ')}`);
        }

        parts.push(`\nОтветь СТРОГО в формате JSON (без markdown обёрток):`);
        parts.push(`{
  "code": "${code}",
  "description": "описание на русском",
  "severity": "info|warning|critical",
  "components": ["meshName компонентов"],
  "possibleCauses": ["причина 1", "причина 2"],
  "procedures": ["шаг 1", "шаг 2"],
  "canDrive": true/false,
  "urgency": "рекомендация"
}`);

        const { text } = await this._request(
            [{ role: 'user', content: parts.join('\n') }],
            {
                systemPrompt: 'Ты автомобильный диагност-эксперт. Анализируй DTC-коды точно и профессионально. Отвечай ТОЛЬКО валидным JSON.'
            }
        );

        try {
            let jsonStr = text.trim()
                .replace(/^```(?:json)?\s*\n?/i, '')
                .replace(/\n?```\s*$/i, '');
            return JSON.parse(jsonStr);
        } catch (e) {
            return {
                code,
                description: text,
                severity: 'info',
                components: [],
                possibleCauses: [],
                procedures: [],
                canDrive: true,
                urgency: 'Требуется дополнительная диагностика'
            };
        }
    }

    /**
     * Проверить доступность API
     * @returns {Promise<boolean>}
     */
    async isAvailable() {
        if (!this._apiKey) return false;
        try {
            await this._request(
                [{ role: 'user', content: 'ping' }],
                { maxTokens: 10 }
            );
            return true;
        } catch (e) {
            return false;
        }
    }

    /**
     * Установить/обновить API ключ
     * @param {string} apiKey
     */
    setApiKey(apiKey) {
        this._apiKey = apiKey || '';
    }

    /**
     * Получить статистику использования текущей сессии
     * @returns {{ requestCount: number, totalTokens: number, errors: number }}
     */
    getUsageStats() {
        return { ...this._stats };
    }

    // ══════════════════════════════════════════════════════════
    // Статические методы для работы с localStorage
    // ══════════════════════════════════════════════════════════

    /**
     * Получить список доступных моделей Claude
     * @returns {Array<{id: string, name: string, description: string}>}
     */
    static getAvailableModels() {
        return [
            { id: 'claude-sonnet-4-5-20250929', name: 'Claude Sonnet 4.5', description: 'Быстрый и точный' },
            { id: 'claude-opus-4-6', name: 'Claude Opus 4.6', description: 'Самый мощный' },
            { id: 'claude-haiku-4-5-20251001', name: 'Claude Haiku 4.5', description: 'Лёгкий и дешёвый' }
        ];
    }

    /**
     * Получить сохранённый API ключ из localStorage
     * @returns {string|null}
     */
    static getStoredApiKey() {
        try {
            return localStorage.getItem(STORAGE_KEY) || null;
        } catch {
            return null;
        }
    }

    /**
     * Сохранить API ключ в localStorage
     * @param {string} key
     */
    static setStoredApiKey(key) {
        try {
            if (key) {
                localStorage.setItem(STORAGE_KEY, key);
            } else {
                localStorage.removeItem(STORAGE_KEY);
            }
        } catch {
            // localStorage недоступен
        }
    }
}
