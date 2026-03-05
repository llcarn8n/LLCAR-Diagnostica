// ══════════════════════════════════════════════════════════
// ComponentKnowledge — модуль базы знаний автодиагностики
// Связывает 3D-меши с DTC-кодами, мануалом, спецификациями
// Работает полностью офлайн (без API)
// ══════════════════════════════════════════════════════════

/**
 * Основной модуль базы знаний для диагностики Li Auto L7/L9
 */
export class ComponentKnowledge {
    /**
     * @param {Object} options
     * @param {string} [options.basePath='../Diagnostica/knowledge-base'] - Путь к JSON-файлам
     */
    constructor(options = {}) {
        this._basePath = options.basePath || '../Diagnostica/knowledge-base';
        this._vehicleModel = null;
        this._loaded = false;

        // Данные
        this._componentMap = null;  // component-map JSON (компоненты, системы, DTC)
        this._config = null;        // config JSON (спецификации автомобиля)
        this._manualSections = null; // manual-sections JSON (разделы мануала)

        // Индексы для быстрого поиска
        this._meshIndex = new Map();       // meshName -> ComponentInfo
        this._dtcIndex = new Map();        // dtcCode -> DtcEntry
        this._systemIndex = new Map();     // systemId -> System
        this._textIndex = [];              // [{text, type, ref}] для полнотекстового поиска
    }

    /**
     * Загрузить данные для конкретной модели автомобиля
     * @param {string} vehicleModel - 'li7' | 'li9'
     * @returns {Promise<void>}
     */
    async load(vehicleModel) {
        const model = vehicleModel.toLowerCase();
        if (model !== 'li7' && model !== 'li9') {
            throw new Error(`Неизвестная модель: ${vehicleModel}. Поддерживаются: li7, li9`);
        }

        this._vehicleModel = model;
        this._loaded = false;

        // Сброс индексов
        this._meshIndex.clear();
        this._dtcIndex.clear();
        this._systemIndex.clear();
        this._textIndex = [];

        // Загрузка JSON файлов
        const prefix = model === 'li7' ? 'l7' : 'l9';
        const loadErrors = [];

        // 1. Config (спецификации)
        try {
            this._config = await this._fetchJSON(`${this._basePath}/${prefix}-config.json`);
        } catch (e) {
            loadErrors.push(`config: ${e.message}`);
            this._config = null;
        }

        // 2. Manual sections
        try {
            this._manualSections = await this._fetchJSON(`${this._basePath}/${prefix}-manual-sections.json`);
        } catch (e) {
            loadErrors.push(`manual: ${e.message}`);
            this._manualSections = null;
        }

        // 3. Component map (основной файл связей — файлы li7/li9)
        try {
            this._componentMap = await this._fetchJSON(`${this._basePath}/${model}-component-map.json`);
        } catch (e) {
            // Component map ещё не создан — работаем на основе config + manual
            loadErrors.push(`component-map: ${e.message}`);
            this._componentMap = null;
        }

        // Построение индексов из того, что загружено
        this._buildIndices();
        this._loaded = true;

        if (loadErrors.length > 0) {
            console.warn(`[ComponentKnowledge] Частичная загрузка для ${model}:`, loadErrors);
        }
    }

    /**
     * Загрузить JSON файл
     * @private
     */
    async _fetchJSON(url) {
        const resp = await fetch(url);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${url}`);
        return resp.json();
    }

    /**
     * Построить поисковые индексы
     * @private
     */
    _buildIndices() {
        // Индекс систем
        if (this._componentMap?.systems) {
            for (const [sysId, sys] of Object.entries(this._componentMap.systems)) {
                this._systemIndex.set(sysId, { ...sys, systemId: sysId });
                // Текстовый индекс
                if (sys.label_ru) {
                    this._textIndex.push({
                        text: sys.label_ru.toLowerCase(),
                        type: 'system',
                        ref: sysId
                    });
                }
            }
        }

        // Индекс компонентов
        if (this._componentMap?.components) {
            for (const [meshName, comp] of Object.entries(this._componentMap.components)) {
                const info = this._buildComponentInfo(meshName, comp);
                this._meshIndex.set(meshName, info);

                // Индекс по дочерним мешам
                if (comp.childMeshes) {
                    for (const child of comp.childMeshes) {
                        this._meshIndex.set(child, { ...info, _isChild: true, _parentMesh: meshName });
                    }
                }

                // Текстовый индекс
                this._textIndex.push({
                    text: (comp.displayName || meshName).toLowerCase(),
                    type: 'component',
                    ref: meshName
                });
                if (comp.description) {
                    this._textIndex.push({
                        text: comp.description.toLowerCase(),
                        type: 'component',
                        ref: meshName
                    });
                }
            }
        }

        // Индекс DTC
        if (this._componentMap?.dtcIndex) {
            for (const [code, entry] of Object.entries(this._componentMap.dtcIndex)) {
                this._dtcIndex.set(code.toUpperCase(), { ...entry, code });
                // Текстовый индекс
                this._textIndex.push({
                    text: `${code} ${(entry.description_ru || '').toLowerCase()}`,
                    type: 'dtc',
                    ref: code
                });
            }
        }

        // Индекс секций мануала
        if (this._manualSections?.chapters) {
            for (const chapter of this._manualSections.chapters) {
                this._textIndex.push({
                    text: (chapter.title || '').toLowerCase(),
                    type: 'manual',
                    ref: chapter.id
                });
                if (chapter.sections) {
                    for (const section of chapter.sections) {
                        this._textIndex.push({
                            text: (section.title || '').toLowerCase(),
                            type: 'manual',
                            ref: chapter.id
                        });
                    }
                }
            }
        }
    }

    /**
     * Собрать ComponentInfo из raw данных
     * @private
     */
    _buildComponentInfo(meshName, comp) {
        const sys = this._systemIndex.get(comp.system);
        return {
            meshName,
            displayName: comp.displayName || meshName,
            system: comp.system || 'unknown',
            systemLabel: sys?.label_ru || comp.system || 'Неизвестно',
            description: comp.description || '',
            dtcCodes: comp.dtcCodes || [],
            manualSections: comp.manualSections || [],
            specs: comp.specs || {},
            selectable: comp.selectable !== false,
            xray_transparent: comp.xray_transparent || false,
            layer_num: comp.layer_num ?? 0,
            childMeshes: comp.childMeshes || [],
            wearParts: comp.wearParts || []
        };
    }

    /**
     * Проверить, загружены ли данные
     * @returns {boolean}
     */
    isLoaded() {
        return this._loaded;
    }

    /**
     * Получить текущую загруженную модель
     * @returns {string|null}
     */
    getCurrentModel() {
        return this._vehicleModel;
    }

    // ══════════════════════════════════════════════════════════
    // ПОИСК ПО DTC-КОДУ
    // ══════════════════════════════════════════════════════════

    /**
     * Поиск информации по DTC-коду
     * @param {string} code - DTC-код (например 'P0300')
     * @returns {Object|null} DtcSearchResult или null
     */
    searchByDTC(code) {
        if (!this._loaded) return null;
        const entry = this._dtcIndex.get(code.toUpperCase());
        if (!entry) return null;

        const components = (entry.components || [])
            .map(name => this._meshIndex.get(name))
            .filter(Boolean);

        const manualSections = (entry.manualSections || [])
            .map(id => this.getManualSection(id))
            .filter(Boolean);

        return {
            code: entry.code,
            description_ru: entry.description_ru || '',
            severity: entry.severity || 'info',
            components,
            manualSections,
            procedures: entry.procedures || [],
            possibleCauses: entry.possibleCauses || []
        };
    }

    /**
     * Поиск по нескольким DTC-кодам
     * @param {string[]} codes
     * @returns {Object[]} Результаты отсортированы по severity
     */
    searchByMultipleDTC(codes) {
        const severityOrder = { critical: 0, warning: 1, info: 2 };
        return codes
            .map(code => this.searchByDTC(code))
            .filter(Boolean)
            .sort((a, b) => (severityOrder[a.severity] ?? 3) - (severityOrder[b.severity] ?? 3));
    }

    // ══════════════════════════════════════════════════════════
    // ПОИСК ПО КОМПОНЕНТУ (клик на 3D модель)
    // ══════════════════════════════════════════════════════════

    /**
     * Получить полную информацию о компоненте по meshName
     * @param {string} meshName
     * @returns {Object|null} ComponentInfo
     */
    getComponentInfo(meshName) {
        if (!this._loaded) return null;
        return this._meshIndex.get(meshName) || null;
    }

    /**
     * Поиск компонента по meshName (с нечётким поиском)
     * @param {string} meshName - Имя кликнутого меша
     * @returns {Object|null} ComponentSearchResult
     */
    searchByComponent(meshName) {
        if (!this._loaded) return null;

        // Точное совпадение
        const direct = this._meshIndex.get(meshName);
        if (direct) {
            if (direct._isChild) {
                const parent = this._meshIndex.get(direct._parentMesh);
                return parent ? {
                    ...parent,
                    clickedMesh: meshName,
                    isChildMesh: true,
                    parentComponent: direct._parentMesh
                } : null;
            }
            return {
                ...direct,
                clickedMesh: meshName,
                isChildMesh: false,
                parentComponent: null
            };
        }

        // Нечёткий поиск — ищем родителя по префиксу
        // Например 'Кузов#2 — Порог' -> ищем 'Кузов#2'
        const baseName = meshName.split(' — ')[0].split(' - ')[0].trim();
        if (baseName !== meshName) {
            const parent = this._meshIndex.get(baseName);
            if (parent) {
                return {
                    ...parent,
                    clickedMesh: meshName,
                    isChildMesh: true,
                    parentComponent: baseName
                };
            }
        }

        // Поиск по подстроке
        for (const [key, info] of this._meshIndex) {
            if (meshName.startsWith(key) || key.startsWith(meshName)) {
                return {
                    ...info,
                    clickedMesh: meshName,
                    isChildMesh: meshName !== key,
                    parentComponent: meshName !== key ? key : null
                };
            }
        }

        return null;
    }

    // ══════════════════════════════════════════════════════════
    // ТЕКСТОВЫЙ ПОИСК
    // ══════════════════════════════════════════════════════════

    /**
     * Полнотекстовый поиск по базе знаний
     * @param {string} query
     * @param {Object} options
     * @param {number} [options.limit=10]
     * @param {string} [options.scope='all'] - 'components' | 'dtc' | 'manual' | 'all'
     * @returns {Array} SearchResult[]
     */
    searchByText(query, options = {}) {
        if (!this._loaded || !query) return [];

        const limit = options.limit || 10;
        const scope = options.scope || 'all';
        const q = query.toLowerCase().trim();
        const words = q.split(/\s+/);

        const results = [];

        for (const entry of this._textIndex) {
            if (scope !== 'all') {
                const scopeMap = { components: 'component', dtc: 'dtc', manual: 'manual' };
                if (entry.type !== scopeMap[scope]) continue;
            }

            // Подсчёт релевантности
            let score = 0;
            const text = entry.text;

            // Полное совпадение
            if (text.includes(q)) {
                score = 1.0;
            } else {
                // Совпадение отдельных слов
                let matched = 0;
                for (const w of words) {
                    if (text.includes(w)) matched++;
                }
                score = words.length > 0 ? matched / words.length : 0;
            }

            if (score <= 0) continue;

            let title = '';
            let snippet = '';
            let meshNames = [];
            let sectionId, dtcCode;

            if (entry.type === 'component') {
                const comp = this._meshIndex.get(entry.ref);
                if (comp) {
                    title = comp.displayName;
                    snippet = comp.description || `Система: ${comp.systemLabel}`;
                    meshNames = [comp.meshName, ...comp.childMeshes];
                }
            } else if (entry.type === 'dtc') {
                const dtc = this._dtcIndex.get(entry.ref);
                if (dtc) {
                    title = `${dtc.code}: ${dtc.description_ru}`;
                    snippet = `Серьёзность: ${dtc.severity}`;
                    meshNames = dtc.components || [];
                    dtcCode = dtc.code;
                }
            } else if (entry.type === 'manual') {
                title = entry.text;
                snippet = `Раздел мануала: ${entry.ref}`;
                sectionId = entry.ref;
            }

            results.push({ type: entry.type, score, title, snippet, meshNames, sectionId, dtcCode });
        }

        // Сортировка по релевантности и дедупликация
        results.sort((a, b) => b.score - a.score);

        const seen = new Set();
        const unique = [];
        for (const r of results) {
            const key = `${r.type}:${r.title}`;
            if (!seen.has(key)) {
                seen.add(key);
                unique.push(r);
                if (unique.length >= limit) break;
            }
        }

        return unique;
    }

    // ══════════════════════════════════════════════════════════
    // НАВИГАЦИЯ ПО СИСТЕМАМ
    // ══════════════════════════════════════════════════════════

    /**
     * Получить список всех систем автомобиля
     * @returns {Array} SystemInfo[]
     */
    getAllSystems() {
        const systems = [];
        for (const [sysId, sys] of this._systemIndex) {
            const components = this._getComponentsBySystemInternal(sysId);
            let dtcCount = 0;
            for (const comp of components) {
                dtcCount += (comp.dtcCodes || []).length;
            }
            systems.push({
                systemId: sysId,
                label_ru: sys.label_ru || sysId,
                color: sys.color || '#888888',
                componentCount: components.length,
                dtcCount
            });
        }
        return systems;
    }

    /**
     * @private
     */
    _getComponentsBySystemInternal(systemId) {
        const components = [];
        for (const [, info] of this._meshIndex) {
            if (info.system === systemId && !info._isChild) {
                components.push(info);
            }
        }
        return components;
    }

    /**
     * Получить компоненты определённой системы
     * @param {string} systemId
     * @returns {Array} ComponentInfo[]
     */
    getComponentsBySystem(systemId) {
        if (!this._loaded) return [];
        return this._getComponentsBySystemInternal(systemId);
    }

    /**
     * Получить цвет подсветки для системы
     * @param {string} systemId
     * @param {'normal'|'warning'|'critical'} [severity='normal']
     * @returns {string} Цвет '#RRGGBB'
     */
    getSystemColor(systemId, severity = 'normal') {
        const colors = this._componentMap?.systemColors?.[systemId];
        if (colors) return colors[severity] || colors.normal || '#888888';

        // Дефолтные цвета
        const defaults = {
            powertrain: '#00CC00', chassis: '#00AAFF', body: '#8888FF',
            electrical: '#FFFF00', battery_hv: '#FF6600', interior: '#CC88FF',
            suspension: '#00DDAA', brakes: '#FF4444', steering: '#44AAFF'
        };
        return defaults[systemId] || '#888888';
    }

    // ══════════════════════════════════════════════════════════
    // ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ
    // ══════════════════════════════════════════════════════════

    /**
     * Получить технические характеристики автомобиля
     * @param {string} [category] - 'dimensions'|'battery'|'powertrain'|'tires'|'brakes'|'suspension' или null
     * @returns {Object}
     */
    getSpecs(category = null) {
        if (!this._config?.specs) return {};
        if (category) return this._config.specs[category] || {};
        return this._config.specs;
    }

    /**
     * Получить гарантийную информацию
     * @returns {Object} WarrantyInfo
     */
    getWarrantyInfo() {
        const w = this._config?.specs?.warranty;
        if (!w) return { vehicle: {}, threeElectric: {}, airSuspension: {}, wearParts: [] };

        return {
            vehicle: { years: 5, km: 100000, raw: w.vehicle },
            threeElectric: { years: 8, km: 160000, raw: w.battery_motor_control },
            airSuspension: { years: 8, km: 160000, raw: w.air_suspension },
            wearParts: []
        };
    }

    // ══════════════════════════════════════════════════════════
    // СЕКЦИИ МАНУАЛА
    // ══════════════════════════════════════════════════════════

    /**
     * Получить секцию мануала по ID
     * @param {string} sectionId
     * @returns {Object|null} ManualSection
     */
    getManualSection(sectionId) {
        if (!this._manualSections?.chapters) return null;
        for (const chapter of this._manualSections.chapters) {
            if (chapter.id === sectionId) {
                return {
                    sectionId: chapter.id,
                    title: chapter.title,
                    content: '',
                    warnings: [],
                    procedures: [],
                    tables: [],
                    pageStart: chapter.start_page,
                    pageEnd: null,
                    sections: chapter.sections || []
                };
            }
        }
        return null;
    }

    /**
     * Получить оглавление мануала
     * @returns {Array} ManualTocEntry[]
     */
    getManualTOC() {
        if (!this._manualSections?.chapters) return [];
        return this._manualSections.chapters.map(ch => ({
            sectionId: ch.id,
            title: ch.title,
            level: 1,
            pageStart: ch.start_page,
            children: (ch.sections || []).map(s => ({
                sectionId: ch.id,
                title: s.title,
                level: 2,
                pageStart: s.page,
                children: []
            }))
        }));
    }
}
