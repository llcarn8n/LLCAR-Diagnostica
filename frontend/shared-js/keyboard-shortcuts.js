/**
 * KeyboardShortcuts - Reusable keyboard shortcuts system for Three.js examples.
 *
 * Usage:
 *   import { KeyboardShortcuts } from '../js/keyboard-shortcuts.js';
 *   const shortcuts = new KeyboardShortcuts();
 *   shortcuts.register('g', () => setTransformMode('translate'), 'Translate mode');
 *   shortcuts.register('ctrl+a', () => selectAll(), 'Select all');
 *   shortcuts.enable();
 */

export class KeyboardShortcuts {
    constructor() {
        this._shortcuts = new Map();
        this._categories = new Map();
        this._enabled = false;
        this._overlayVisible = false;
        this._overlay = null;
        this._toastEl = null;
        this._handler = this._onKeyDown.bind(this);
    }

    /**
     * Register a shortcut.
     * @param {string} combo - Key combo, e.g. 'g', 'ctrl+a', 'shift+h', 'delete'
     * @param {Function} callback - Function to call
     * @param {string} description - Human-readable description
     * @param {string} [category='General'] - Category for help overlay grouping
     */
    register(combo, callback, description, category = 'General') {
        const key = this._normalizeCombo(combo);
        this._shortcuts.set(key, { callback, description, combo, category });
        if (!this._categories.has(category)) {
            this._categories.set(category, []);
        }
        this._categories.get(category).push({ combo, description, key });
    }

    /**
     * Unregister a shortcut.
     */
    unregister(combo) {
        const key = this._normalizeCombo(combo);
        const entry = this._shortcuts.get(key);
        if (entry) {
            this._shortcuts.delete(key);
            const cat = this._categories.get(entry.category);
            if (cat) {
                const idx = cat.findIndex(c => c.key === key);
                if (idx !== -1) cat.splice(idx, 1);
            }
        }
    }

    enable() {
        if (!this._enabled) {
            document.addEventListener('keydown', this._handler);
            this._enabled = true;
        }
    }

    disable() {
        if (this._enabled) {
            document.removeEventListener('keydown', this._handler);
            this._enabled = false;
        }
    }

    _normalizeCombo(combo) {
        return combo.toLowerCase().split('+').sort().join('+');
    }

    _eventToCombo(e) {
        const parts = [];
        if (e.ctrlKey || e.metaKey) parts.push('ctrl');
        if (e.shiftKey) parts.push('shift');
        if (e.altKey) parts.push('alt');

        let key = e.key.toLowerCase();
        // Normalize special keys
        if (key === ' ') key = 'space';
        if (key === 'arrowup') key = 'up';
        if (key === 'arrowdown') key = 'down';
        if (key === 'arrowleft') key = 'left';
        if (key === 'arrowright') key = 'right';

        if (!['ctrl', 'shift', 'alt', 'meta', 'control'].includes(key)) {
            parts.push(key);
        }
        return parts.sort().join('+');
    }

    _isInputFocused() {
        const el = document.activeElement;
        if (!el) return false;
        const tag = el.tagName.toLowerCase();
        return tag === 'input' || tag === 'textarea' || tag === 'select' || el.isContentEditable;
    }

    _onKeyDown(e) {
        // Don't intercept when user is typing in inputs
        if (this._isInputFocused()) return;

        // Toggle help overlay on ? or F1
        if (e.key === '?' || e.key === 'F1') {
            e.preventDefault();
            this.toggleHelp();
            return;
        }

        // Close overlay on Escape
        if (e.key === 'Escape' && this._overlayVisible) {
            this.hideHelp();
            return;
        }

        const combo = this._eventToCombo(e);
        const entry = this._shortcuts.get(combo);
        if (entry) {
            e.preventDefault();
            entry.callback();
            this.showToast(entry.description);
        }
    }

    // --- Toast notifications ---

    showToast(message) {
        if (!this._toastEl) {
            this._toastEl = document.createElement('div');
            Object.assign(this._toastEl.style, {
                position: 'fixed',
                bottom: '60px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(18, 18, 26, 0.92)',
                backdropFilter: 'blur(16px)',
                color: '#e0e0e8',
                padding: '10px 24px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: '500',
                fontFamily: 'Inter, -apple-system, sans-serif',
                border: '1px solid rgba(255,255,255,0.06)',
                boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
                zIndex: '10000',
                pointerEvents: 'none',
                opacity: '0',
                transition: 'opacity 0.15s ease'
            });
            document.body.appendChild(this._toastEl);
        }

        this._toastEl.textContent = message;
        this._toastEl.style.opacity = '1';

        clearTimeout(this._toastTimeout);
        this._toastTimeout = setTimeout(() => {
            if (this._toastEl) this._toastEl.style.opacity = '0';
        }, 1500);
    }

    // --- Help overlay ---

    toggleHelp() {
        if (this._overlayVisible) {
            this.hideHelp();
        } else {
            this.showHelp();
        }
    }

    showHelp() {
        if (this._overlay) this._overlay.remove();

        this._overlay = document.createElement('div');
        Object.assign(this._overlay.style, {
            position: 'fixed',
            top: '0', left: '0', right: '0', bottom: '0',
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(8px)',
            zIndex: '9999',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'Inter, -apple-system, sans-serif'
        });

        const panel = document.createElement('div');
        Object.assign(panel.style, {
            background: 'rgba(18, 18, 26, 0.98)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '16px',
            padding: '32px',
            maxWidth: '600px',
            width: '90vw',
            maxHeight: '80vh',
            overflowY: 'auto',
            color: '#e0e0e8',
            boxShadow: '0 16px 64px rgba(0,0,0,0.5)'
        });

        let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">';
        html += '<h2 style="margin:0;font-size:18px;font-weight:600;">Keyboard Shortcuts</h2>';
        html += '<span id="close-shortcuts" style="cursor:pointer;color:#888;font-size:22px;padding:4px 8px;">&times;</span>';
        html += '</div>';

        for (const [category, shortcuts] of this._categories) {
            if (shortcuts.length === 0) continue;
            html += `<h3 style="font-size:11px;font-weight:600;color:#555568;text-transform:uppercase;letter-spacing:0.8px;margin:20px 0 10px;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.06);">${category}</h3>`;
            html += '<div style="display:grid;grid-template-columns:120px 1fr;gap:6px 16px;">';
            shortcuts.forEach(s => {
                const keys = s.combo.split('+').map(k =>
                    `<kbd style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:4px;padding:2px 8px;font-size:12px;font-family:inherit;color:#a29bfe;">${k.charAt(0).toUpperCase() + k.slice(1)}</kbd>`
                ).join(' + ');
                html += `<div style="text-align:right;">${keys}</div>`;
                html += `<div style="font-size:13px;color:#8888a0;">${s.description}</div>`;
            });
            html += '</div>';
        }

        html += '<div style="margin-top:24px;text-align:center;font-size:11px;color:#555568;">Press <kbd style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:4px;padding:2px 6px;font-size:11px;color:#a29bfe;">?</kbd> or <kbd style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:4px;padding:2px 6px;font-size:11px;color:#a29bfe;">Esc</kbd> to close</div>';

        panel.innerHTML = html;
        this._overlay.appendChild(panel);
        document.body.appendChild(this._overlay);

        // Close on backdrop click
        this._overlay.addEventListener('click', (e) => {
            if (e.target === this._overlay) this.hideHelp();
        });

        // Close button
        panel.querySelector('#close-shortcuts').addEventListener('click', () => this.hideHelp());

        this._overlayVisible = true;
    }

    hideHelp() {
        if (this._overlay) {
            this._overlay.remove();
            this._overlay = null;
        }
        this._overlayVisible = false;
    }

    destroy() {
        this.disable();
        this.hideHelp();
        if (this._toastEl) {
            this._toastEl.remove();
            this._toastEl = null;
        }
        this._shortcuts.clear();
        this._categories.clear();
    }
}
