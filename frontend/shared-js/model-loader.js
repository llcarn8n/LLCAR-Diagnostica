// Общий модуль для загрузки GLB моделей во всех примерах
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as THREE from 'three';

/**
 * Recursively disposes all geometries, materials, and textures in a Three.js object tree.
 */
export function disposeObject(obj) {
    if (!obj) return;
    obj.traverse((node) => {
        if (node.geometry) {
            node.geometry.dispose();
        }
        if (node.material) {
            const materials = Array.isArray(node.material) ? node.material : [node.material];
            materials.forEach(mat => {
                if (mat.map) mat.map.dispose();
                if (mat.normalMap) mat.normalMap.dispose();
                if (mat.roughnessMap) mat.roughnessMap.dispose();
                if (mat.metalnessMap) mat.metalnessMap.dispose();
                if (mat.aoMap) mat.aoMap.dispose();
                if (mat.emissiveMap) mat.emissiveMap.dispose();
                if (mat.envMap) mat.envMap.dispose();
                mat.dispose();
            });
        }
    });
}

export class ModelLoader {
    constructor(scene) {
        this.scene = scene;
        this.loadedModel = null;
        this.loader = new GLTFLoader();
    }

    loadFromFile(file, onSuccess, onError) {
        if (!file.name.toLowerCase().endsWith('.glb') && !file.name.toLowerCase().endsWith('.gltf')) {
            if (onError) onError('Пожалуйста, выберите файл в формате GLB или GLTF');
            return;
        }

        const url = URL.createObjectURL(file);

        this.loader.load(
            url,
            (gltf) => {
                // Удаляем предыдущую модель
                if (this.loadedModel) {
                    this.scene.remove(this.loadedModel);
                    disposeObject(this.loadedModel);
                }

                this.loadedModel = gltf.scene;

                // Центрируем и масштабируем модель
                const box = new THREE.Box3().setFromObject(this.loadedModel);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 4 / maxDim;

                this.loadedModel.scale.multiplyScalar(scale);
                this.loadedModel.position.sub(center.multiplyScalar(scale));

                this.loadedModel.traverse((node) => {
                    if (node.isMesh) {
                        node.castShadow = true;
                        node.receiveShadow = true;
                    }
                });

                this.scene.add(this.loadedModel);

                if (onSuccess) onSuccess(this.loadedModel, file);

                URL.revokeObjectURL(url);
            },
            undefined,
            (error) => {
                console.error('Ошибка загрузки модели:', error);
                if (onError) onError('Ошибка загрузки модели!');
            }
        );
    }

    removeModel() {
        if (this.loadedModel) {
            this.scene.remove(this.loadedModel);
            disposeObject(this.loadedModel);
            this.loadedModel = null;
        }
    }

    getModel() {
        return this.loadedModel;
    }
}
