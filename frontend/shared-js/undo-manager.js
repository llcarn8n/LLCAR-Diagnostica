/**
 * UndoManager - Command-pattern undo/redo system for Three.js examples.
 *
 * Usage:
 *   import { UndoManager, TransformCommand, MaterialCommand, VisibilityCommand } from '../js/undo-manager.js';
 *   const undo = new UndoManager();
 *   undo.execute(new TransformCommand(mesh, oldPos, newPos, oldRot, newRot, oldScale, newScale));
 *   undo.undo();
 *   undo.redo();
 */

import * as THREE from 'three';

export class UndoManager {
    constructor(maxHistory = 50) {
        this.undoStack = [];
        this.redoStack = [];
        this.maxHistory = maxHistory;
        this._listeners = [];
    }

    execute(command) {
        command.execute();
        this.undoStack.push(command);
        this.redoStack = [];
        if (this.undoStack.length > this.maxHistory) {
            this.undoStack.shift();
        }
        this._notify();
    }

    undo() {
        const cmd = this.undoStack.pop();
        if (cmd) {
            cmd.undo();
            this.redoStack.push(cmd);
            this._notify();
            return cmd.description;
        }
        return null;
    }

    redo() {
        const cmd = this.redoStack.pop();
        if (cmd) {
            cmd.execute();
            this.undoStack.push(cmd);
            this._notify();
            return cmd.description;
        }
        return null;
    }

    canUndo() {
        return this.undoStack.length > 0;
    }

    canRedo() {
        return this.redoStack.length > 0;
    }

    clear() {
        this.undoStack = [];
        this.redoStack = [];
        this._notify();
    }

    getHistory() {
        return this.undoStack.map(cmd => cmd.description);
    }

    onChange(fn) {
        this._listeners.push(fn);
    }

    _notify() {
        this._listeners.forEach(fn => fn(this));
    }
}

/**
 * TransformCommand - captures position, rotation, scale changes.
 */
export class TransformCommand {
    constructor(object, oldState, newState) {
        this.object = object;
        this.oldPos = oldState.position.clone();
        this.oldRot = oldState.rotation.clone();
        this.oldScale = oldState.scale.clone();
        this.newPos = newState.position.clone();
        this.newRot = newState.rotation.clone();
        this.newScale = newState.scale.clone();
        this.description = `Transform: ${object.name || 'Object'}`;
    }

    execute() {
        this.object.position.copy(this.newPos);
        this.object.rotation.copy(this.newRot);
        this.object.scale.copy(this.newScale);
    }

    undo() {
        this.object.position.copy(this.oldPos);
        this.object.rotation.copy(this.oldRot);
        this.object.scale.copy(this.oldScale);
    }
}

/**
 * MaterialCommand - captures material property changes on one or more objects.
 */
export class MaterialCommand {
    constructor(objects, propName, oldValues, newValue) {
        this.objects = [...objects];
        this.propName = propName;
        this.oldValues = oldValues; // Map: object -> old value
        this.newValue = newValue;
        this.description = `Material: ${propName}`;
    }

    execute() {
        this.objects.forEach(obj => {
            const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
            mats.forEach(m => {
                if (this.propName === 'color' && m.color) {
                    m.color.set(this.newValue);
                } else if (this.propName === 'opacity' && m.opacity !== undefined) {
                    m.opacity = this.newValue;
                    m.transparent = this.newValue < 1;
                } else if (m[this.propName] !== undefined) {
                    m[this.propName] = this.newValue;
                }
                m.needsUpdate = true;
            });
        });
    }

    undo() {
        this.objects.forEach(obj => {
            const oldVal = this.oldValues.get(obj);
            if (oldVal === undefined) return;
            const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
            mats.forEach(m => {
                if (this.propName === 'color' && m.color) {
                    m.color.set(oldVal);
                } else if (this.propName === 'opacity' && m.opacity !== undefined) {
                    m.opacity = oldVal;
                    m.transparent = oldVal < 1;
                } else if (m[this.propName] !== undefined) {
                    m[this.propName] = oldVal;
                }
                m.needsUpdate = true;
            });
        });
    }
}

/**
 * VisibilityCommand - captures visibility changes.
 */
export class VisibilityCommand {
    constructor(objects, visible) {
        this.objects = [...objects];
        this.oldStates = new Map();
        this.objects.forEach(o => this.oldStates.set(o, o.visible));
        this.newVisible = visible;
        this.description = visible ? 'Show objects' : 'Hide objects';
    }

    execute() {
        this.objects.forEach(o => o.visible = this.newVisible);
    }

    undo() {
        this.objects.forEach(o => {
            const old = this.oldStates.get(o);
            if (old !== undefined) o.visible = old;
        });
    }
}

/**
 * DeleteCommand - captures object deletion for undo.
 */
export class DeleteCommand {
    constructor(objects, scene, allMeshesRef) {
        this.objects = [...objects];
        this.scene = scene;
        this.allMeshesRef = allMeshesRef; // { meshes: [] } - mutable reference
        this.parents = new Map();
        this.objects.forEach(o => this.parents.set(o, o.parent));
        this.description = `Delete ${objects.length} object(s)`;
    }

    execute() {
        this.objects.forEach(o => {
            if (o.parent) o.parent.remove(o);
        });
        this.allMeshesRef.meshes = this.allMeshesRef.meshes.filter(m => !this.objects.includes(m));
    }

    undo() {
        this.objects.forEach(o => {
            const parent = this.parents.get(o) || this.scene;
            parent.add(o);
            if (!this.allMeshesRef.meshes.includes(o)) {
                this.allMeshesRef.meshes.push(o);
            }
        });
    }
}
