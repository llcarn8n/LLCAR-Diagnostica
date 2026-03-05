/**
 * ViewModes - Switchable rendering modes for Three.js meshes.
 *
 * Modes: solid, wireframe, wireframe-overlay, xray, normals, matcap
 *
 * Usage:
 *   import { ViewModes } from '../js/view-modes.js';
 *   const viewModes = new ViewModes(scene);
 *   viewModes.setMode('xray');
 *   viewModes.setMode('solid'); // restores originals
 */

import * as THREE from 'three';

// Embedded base64 matcap texture (small 64x64 neutral gray/blue matcap)
const MATCAP_DATA_URL = (() => {
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createRadialGradient(64, 56, 8, 64, 64, 64);
    grad.addColorStop(0, '#e8e8f0');
    grad.addColorStop(0.3, '#b0b8d0');
    grad.addColorStop(0.6, '#7080a8');
    grad.addColorStop(0.85, '#405080');
    grad.addColorStop(1, '#283048');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 128, 128);
    return canvas.toDataURL();
})();

export class ViewModes {
    constructor() {
        this._currentMode = 'solid';
        this._originalMaterials = new WeakMap();
        this._wireframeOverlays = new Map();
        this._matcapTexture = null;
    }

    get currentMode() {
        return this._currentMode;
    }

    /**
     * Set view mode for all meshes found by traversing the scene.
     * @param {string} mode - 'solid' | 'wireframe' | 'wireframe-overlay' | 'xray' | 'normals' | 'matcap'
     * @param {THREE.Object3D[]} meshes - Array of meshes to apply to
     */
    setMode(mode, meshes) {
        // First, restore to solid to clean up any previous mode
        if (this._currentMode !== 'solid') {
            this._restoreSolid(meshes);
        }

        this._currentMode = mode;

        switch (mode) {
            case 'solid':
                // Already restored above
                break;
            case 'wireframe':
                this._applyWireframe(meshes);
                break;
            case 'wireframe-overlay':
                this._applyWireframeOverlay(meshes);
                break;
            case 'xray':
                this._applyXRay(meshes);
                break;
            case 'normals':
                this._applyNormals(meshes);
                break;
            case 'matcap':
                this._applyMatcap(meshes);
                break;
        }
    }

    _storeMaterial(mesh) {
        if (!this._originalMaterials.has(mesh)) {
            this._originalMaterials.set(mesh, mesh.material);
        }
    }

    _restoreSolid(meshes) {
        meshes.forEach(mesh => {
            const original = this._originalMaterials.get(mesh);
            if (original) {
                mesh.material = original;
                mesh.material.wireframe = false;
                if (mesh.material.transparent !== undefined) {
                    // Don't change transparency - the original material knows its state
                }
                mesh.material.needsUpdate = true;
            }
        });

        // Remove wireframe overlays
        this._wireframeOverlays.forEach((line, mesh) => {
            mesh.remove(line);
            line.geometry.dispose();
            line.material.dispose();
        });
        this._wireframeOverlays.clear();
    }

    _applyWireframe(meshes) {
        meshes.forEach(mesh => {
            this._storeMaterial(mesh);
            mesh.material = mesh.material.clone();
            mesh.material.wireframe = true;
            mesh.material.needsUpdate = true;
        });
    }

    _applyWireframeOverlay(meshes) {
        meshes.forEach(mesh => {
            this._storeMaterial(mesh);
            // Keep solid material, add wireframe lines on top
            const wireGeo = new THREE.WireframeGeometry(mesh.geometry);
            const wireMat = new THREE.LineBasicMaterial({
                color: 0x4ecdc4,
                transparent: true,
                opacity: 0.4,
                depthTest: true
            });
            const wireLines = new THREE.LineSegments(wireGeo, wireMat);
            mesh.add(wireLines);
            this._wireframeOverlays.set(mesh, wireLines);
        });
    }

    _applyXRay(meshes) {
        meshes.forEach(mesh => {
            this._storeMaterial(mesh);
            const original = this._originalMaterials.get(mesh);
            const color = original.color ? original.color.clone() : new THREE.Color(0x6688cc);
            mesh.material = new THREE.MeshBasicMaterial({
                color: color,
                transparent: true,
                opacity: 0.25,
                depthWrite: false,
                side: THREE.DoubleSide,
                wireframe: false
            });

            // Add visible edges
            const edgeGeo = new THREE.EdgesGeometry(mesh.geometry, 30);
            const edgeMat = new THREE.LineBasicMaterial({
                color: 0xaabbdd,
                transparent: true,
                opacity: 0.6
            });
            const edgeLines = new THREE.LineSegments(edgeGeo, edgeMat);
            mesh.add(edgeLines);
            this._wireframeOverlays.set(mesh, edgeLines);
        });
    }

    _applyNormals(meshes) {
        meshes.forEach(mesh => {
            this._storeMaterial(mesh);
            mesh.material = new THREE.MeshNormalMaterial({
                flatShading: false
            });
        });
    }

    _applyMatcap(meshes) {
        if (!this._matcapTexture) {
            this._matcapTexture = new THREE.TextureLoader().load(MATCAP_DATA_URL);
        }
        meshes.forEach(mesh => {
            this._storeMaterial(mesh);
            mesh.material = new THREE.MeshMatcapMaterial({
                matcap: this._matcapTexture
            });
        });
    }

    destroy() {
        if (this._matcapTexture) {
            this._matcapTexture.dispose();
            this._matcapTexture = null;
        }
        this._wireframeOverlays.forEach((line) => {
            line.geometry.dispose();
            line.material.dispose();
        });
        this._wireframeOverlays.clear();
    }
}
