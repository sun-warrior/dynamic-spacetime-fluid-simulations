// Copyright 2026 Rohit Vasant Khakhrodiya
// SPDX-License-Identifier: Apache-2.0

import * as THREE from 'three';
import { io } from 'socket.io-client';
import GUI from 'lil-gui';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 70, 120); 
camera.lookAt(0, -10, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const hud = document.createElement('div');
hud.style.position = 'absolute';
hud.style.bottom = '20px';
hud.style.left = '20px';
hud.style.color = '#ffffff';
hud.style.fontFamily = 'monospace';
hud.style.backgroundColor = 'rgba(0, 0, 0, 0.75)';
hud.style.padding = '20px';
hud.style.borderRadius = '8px';
hud.style.border = '1px solid #444';
hud.style.pointerEvents = 'none';
hud.innerHTML = 'Waiting for tensor stream...';
document.body.appendChild(hud);

const geometry = new THREE.PlaneGeometry(100, 100, 99, 99);

const dsfMaterial = new THREE.MeshBasicMaterial({ color: 0x00ffcc, wireframe: true, transparent: true, opacity: 0.8 });
const dsfPlane = new THREE.Mesh(geometry.clone(), dsfMaterial);
dsfPlane.rotation.x = -Math.PI / 2;
dsfPlane.position.x = -55; 
scene.add(dsfPlane);

const grMaterial = new THREE.MeshBasicMaterial({ color: 0xff3333, wireframe: true, transparent: true, opacity: 0.8 });
const grPlane = new THREE.Mesh(geometry.clone(), grMaterial);
grPlane.rotation.x = -Math.PI / 2;
grPlane.position.x = 55; 
scene.add(grPlane);

const socket = io('http://localhost:3000');
const gui = new GUI({ title: 'Simulation Parameters' });

const params = {
    massDensity: 50.0,
    baseViscosity: 1.0,
    beta: 0.5,           
    alphaHiggs: 0.5,     
    showDSF: true,
    showGR: true
};

const sendParamsToBackend = () => {
    socket.emit('update_params', {
        mass_density: params.massDensity,
        base_viscosity: params.baseViscosity,
        beta: params.beta,
        alpha_higgs: params.alphaHiggs
    });
};

gui.add(params, 'massDensity', 1, 100).name('Mass Density (ρm)').onFinishChange(sendParamsToBackend);
gui.add(params, 'baseViscosity', 0.1, 5.0).name('Base Viscosity (μ₀)').onFinishChange(sendParamsToBackend);
gui.add(params, 'beta', 0.01, 2.0).name('Fluid Coupling (β)').onFinishChange(sendParamsToBackend);
gui.add(params, 'alphaHiggs', 0.01, 2.0).name('Higgs Absorption (α)').onFinishChange(sendParamsToBackend);
gui.add(params, 'showDSF').name('Toggle DSF Model').onChange((val) => dsfPlane.visible = val);
gui.add(params, 'showGR').name('Toggle GR Model').onChange((val) => grPlane.visible = val);

socket.on('connect', () => {
    sendParamsToBackend();
});

socket.on('tensor_stream', (data) => {
    try {
        const dsfData = data.dsf_z;
        const grData = data.gr_z;
        
        let minGrZ = 0;
        let minDsfZ = 0;

        const dsfPositions = dsfPlane.geometry.attributes.position.array;
        const grPositions = grPlane.geometry.attributes.position.array;
        
        let gridIndex = 0;
        
        for (let i = 0; i < dsfPositions.length; i += 3) {
            if (dsfData) {
                const z = dsfData[gridIndex];
                dsfPositions[i + 2] = z;
                if (z < minDsfZ) minDsfZ = z;
            }
            if (grData) {
                const z = grData[gridIndex];
                grPositions[i + 2] = z;
                if (z < minGrZ) minGrZ = z;
            }
            gridIndex++;
        }
        
        hud.innerHTML = `
            <h3 style="margin-top:0; border-bottom: 1px solid #444; padding-bottom: 5px;">Spacetime Geometry Metrics</h3>
            <p><span style="color:#ff3333;">■</span> <b>GR Max Curvature (Depth):</b> ${minGrZ.toFixed(4)} units</p>
            <p><span style="color:#00ffcc;">■</span> <b>DSF Max Curvature (Depth):</b> ${minDsfZ.toFixed(4)} units</p>
            <p><b>Schwarzschild Radius (r_s):</b> ${data.rs ? data.rs.toExponential(4) : 'N/A'}</p>
        `;
        
        dsfPlane.geometry.attributes.position.needsUpdate = true;
        grPlane.geometry.attributes.position.needsUpdate = true;
    } catch (err) {
        console.error("Error parsing stream data:", err);
    }
});

function animate() {
    requestAnimationFrame(animate);
    scene.rotation.y += 0.002; 
    renderer.render(scene, camera);
}

animate();

window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
});