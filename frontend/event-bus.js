/**
 * Event Bus — thin wrapper around document CustomEvent dispatch.
 * Usage:
 *   import { emit, on, off } from './event-bus.js';
 *   on('component:select', (e) => console.log(e.detail));
 *   emit('component:select', { glossaryId: 'intake_manifold@engine' });
 */

export function emit(eventName, detail = {}) {
  document.dispatchEvent(new CustomEvent(eventName, { detail }));
}

export function on(eventName, handler) {
  document.addEventListener(eventName, handler);
}

export function off(eventName, handler) {
  document.removeEventListener(eventName, handler);
}
