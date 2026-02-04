# Three.js Particle Effects + Sentience HUD - Complete Examples

This document shows practical, copy-paste ready examples for integrating Three.js particle effects with the voidOS Sentience HUD system.

## Example 1: Standalone HTML (No Build Required)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentience Nebula</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; background: #000; }
        canvas { display: block; }
        #ui {
            position: fixed; top: 20px; left: 20px; right: 20px;
            color: #00ff88; font-family: monospace;
            background: rgba(0,0,0,0.7); padding: 15px;
            border: 1px solid #00ff88; border-radius: 5px;
        }
        button {
            margin-top: 10px; padding: 8px 16px;
            background: #00ff88; color: #000; border: none;
            border-radius: 3px; cursor: pointer; font-weight: bold;
        }
        button:hover { background: #00dd77; }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <div id="ui">
        <div>Sentience Nebula - Click buttons to change effects</div>
        <div>
            <button onclick="switchEffect('nebula')">Nebula</button>
            <button onclick="switchEffect('reactive')">Mouse Reactive</button>
            <button onclick="switchEffect('explosion')">Explosion</button>
        </div>
        <div id="stats" style="margin-top: 10px; font-size: 12px;"></div>
    </div>

    <script type="module">
        import * as THREE from 'https://cdn.jsdelivr.net/npm/three@r128/build/three.module.js';

        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 2000);
        camera.position.z = 80;

        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas'), antialias: true });
        renderer.setSize(innerWidth, innerHeight);
        renderer.setClearColor(0x0a0a0f);

        let particles = null;
        let currentEffect = 'nebula';
        let frameCount = 0;
        let fps = 0;

        // Create nebula effect
        function createNebula() {
            if (particles) scene.remove(particles);

            const count = 12000;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(count * 3);
            const colors = new Float32Array(count * 3);

            for (let i = 0; i < count; i++) {
                const i3 = i * 3;
                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos(2 * Math.random() - 1);
                const r = 30 + Math.random() * 40;

                positions[i3] = r * Math.sin(phi) * Math.cos(theta);
                positions[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                positions[i3 + 2] = r * Math.cos(phi);

                const t = Math.random();
                const c1 = new THREE.Color(0x8b5cf6).lerp(new THREE.Color(0x60a5fa), t);
                colors[i3] = c1.r;
                colors[i3 + 1] = c1.g;
                colors[i3 + 2] = c1.b;
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const material = new THREE.PointsMaterial({
                size: 0.8,
                vertexColors: true,
                transparent: true,
                opacity: 0.9,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });

            particles = new THREE.Points(geometry, material);
            scene.add(particles);
        }

        // Create reactive effect
        function createReactive() {
            if (particles) scene.remove(particles);

            const count = 8000;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(count * 3);
            const colors = new Float32Array(count * 3);

            for (let i = 0; i < count; i++) {
                const i3 = i * 3;
                positions[i3] = (Math.random() - 0.5) * 200;
                positions[i3 + 1] = (Math.random() - 0.5) * 200;
                positions[i3 + 2] = (Math.random() - 0.5) * 100;

                const t = Math.random();
                const c1 = new THREE.Color(0x00ff88).lerp(new THREE.Color(0xff00ff), t);
                colors[i3] = c1.r;
                colors[i3 + 1] = c1.g;
                colors[i3 + 2] = c1.b;
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const material = new THREE.PointsMaterial({
                size: 1,
                vertexColors: true,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });

            particles = new THREE.Points(geometry, material);
            particles.userData.original = positions.slice();
            scene.add(particles);
        }

        // Create explosion effect
        function createExplosion() {
            if (particles) scene.remove(particles);

            const count = 5000;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(count * 3);
            const colors = new Float32Array(count * 3);
            const velocities = new Float32Array(count * 3);

            for (let i = 0; i < count; i++) {
                positions[i * 3] = 0;
                positions[i * 3 + 1] = 0;
                positions[i * 3 + 2] = 0;

                const theta = Math.random() * Math.PI * 2;
                const phi = Math.acos(2 * Math.random() - 1);
                const speed = 0.5 + Math.random();

                velocities[i * 3] = Math.sin(phi) * Math.cos(theta) * speed;
                velocities[i * 3 + 1] = Math.sin(phi) * Math.sin(theta) * speed;
                velocities[i * 3 + 2] = Math.cos(phi) * speed;

                const t = Math.random();
                const c1 = new THREE.Color(0xff4444).lerp(new THREE.Color(0xffaa00), t);
                colors[i * 3] = c1.r;
                colors[i * 3 + 1] = c1.g;
                colors[i * 3 + 2] = c1.b;
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            const material = new THREE.PointsMaterial({
                size: 1.2,
                vertexColors: true,
                transparent: true,
                opacity: 0.9,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });

            particles = new THREE.Points(geometry, material);
            particles.userData.velocities = velocities;
            particles.userData.time = 0;
            scene.add(particles);
        }

        // Global effect switcher
        window.switchEffect = (effect) => {
            currentEffect = effect;
            if (effect === 'nebula') createNebula();
            else if (effect === 'reactive') createReactive();
            else if (effect === 'explosion') createExplosion();
        };

        // Mouse tracking for reactive mode
        const mouse = new THREE.Vector2();
        window.addEventListener('mousemove', (e) => {
            mouse.x = (e.clientX / innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / innerHeight) * 2 + 1;
        });

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            frameCount++;

            if (particles) {
                if (currentEffect === 'nebula') {
                    particles.rotation.y += 0.0004;
                    particles.rotation.x += 0.0002;
                }
                else if (currentEffect === 'reactive') {
                    const pos = particles.geometry.attributes.position.array;
                    const orig = particles.userData.original;
                    for (let i = 0; i < pos.length; i += 3) {
                        const tx = mouse.x * 30;
                        const ty = mouse.y * 30;
                        pos[i] += (tx - pos[i]) * 0.01;
                        pos[i + 1] += (ty - pos[i + 1]) * 0.01;
                    }
                    particles.geometry.attributes.position.needsUpdate = true;
                }
                else if (currentEffect === 'explosion') {
                    particles.userData.time += 0.016;
                    const pos = particles.geometry.attributes.position.array;
                    const vel = particles.userData.velocities;
                    for (let i = 0; i < pos.length; i += 3) {
                        pos[i] += vel[i] * 0.2;
                        pos[i + 1] += vel[i + 1] * 0.2;
                        pos[i + 2] += vel[i + 2] * 0.2;
                        vel[i + 1] -= 0.008;
                    }
                    particles.geometry.attributes.position.needsUpdate = true;
                    if (particles.userData.time > 3) {
                        createExplosion();
                    }
                }
            }

            renderer.render(scene, camera);

            if (frameCount % 60 === 0) {
                fps = frameCount;
                frameCount = 0;
                document.getElementById('stats').textContent = `Effect: ${currentEffect} | FPS: ${fps}`;
            }
        }

        animate();

        // Handle resize
        window.addEventListener('resize', () => {
            camera.aspect = innerWidth / innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(innerWidth, innerHeight);
        });

        // Start with nebula
        createNebula();
    </script>
</body>
</html>
```

## Example 2: React Component Integration

```jsx
import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const ParticleBackground = ({ effect = 'nebula' }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      2000
    );
    camera.position.z = 80;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x0a0a0f);
    mountRef.current.appendChild(renderer.domElement);

    sceneRef.current = { scene, camera, renderer };

    const createParticles = () => {
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(12000 * 3);
      const colors = new Float32Array(12000 * 3);

      for (let i = 0; i < 12000; i++) {
        const i3 = i * 3;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        const r = 30 + Math.random() * 40;

        positions[i3] = r * Math.sin(phi) * Math.cos(theta);
        positions[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        positions[i3 + 2] = r * Math.cos(phi);

        const t = Math.random();
        const c = new THREE.Color(0x8b5cf6).lerp(new THREE.Color(0x60a5fa), t);
        colors[i3] = c.r;
        colors[i3 + 1] = c.g;
        colors[i3 + 2] = c.b;
      }

      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

      const material = new THREE.PointsMaterial({
        size: 0.8,
        vertexColors: true,
        transparent: true,
        opacity: 0.9,
        blending: THREE.AdditiveBlending
      });

      return new THREE.Points(geometry, material);
    };

    const particles = createParticles();
    scene.add(particles);

    const animate = () => {
      requestAnimationFrame(animate);
      particles.rotation.y += 0.0003;
      particles.rotation.x += 0.0001;
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, [effect]);

  return <div ref={mountRef} style={{ width: '100%', height: '100%' }} />;
};

export default ParticleBackground;
```

## Example 3: Integration with voidOS Sentience HUD

```python
# In voidos_sentience.py, modify the HTML to include particle selector

ENHANCED_DASHBOARD_HTML = """
<html>
<head>
    <style>
        .particle-controls {
            position: fixed; bottom: 20px; right: 20px;
            background: rgba(0,0,0,0.8); border: 1px solid #00ff88;
            padding: 15px; border-radius: 5px; z-index: 1000;
        }
        .particle-btn {
            display: block; width: 100%;
            margin: 5px 0; padding: 8px;
            background: rgba(0,255,136,0.1); border: 1px solid #00ff88;
            color: #00ff88; cursor: pointer; border-radius: 3px;
        }
        .particle-btn.active {
            background: rgba(0,255,136,0.3);
        }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <div class="particle-controls">
        <button class="particle-btn active" onclick="switchParticleEffect('nebula')">
            Nebula
        </button>
        <button class="particle-btn" onclick="switchParticleEffect('reactive')">
            Mouse Reactive
        </button>
        <button class="particle-btn" onclick="switchParticleEffect('explosion')">
            Explosion
        </button>
    </div>
    
    <script type="module">
        import * as THREE from 'https://cdn.jsdelivr.net/npm/three@r128/build/three.module.js';
        // ... particle code here
    </script>
</body>
</html>
"""

# Then update DashboardHandler.do_GET()
def do_GET(self):
    if self.path == '/':
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(ENHANCED_DASHBOARD_HTML.encode())
```

## Example 4: Advanced - GPU Accelerated Particles

```javascript
// For high-performance systems, use WebGL texture-based particles

import * as THREE from 'three';

class GPUParticleSystem {
    constructor(scene, count = 50000) {
        this.count = count;
        this.scene = scene;
        
        // Create texture for particle data
        const canvas = document.createElement('canvas');
        canvas.width = Math.ceil(Math.sqrt(count));
        canvas.height = canvas.width;
        
        const ctx = canvas.getContext('2d');
        const imgData = ctx.createImageData(canvas.width, canvas.height);
        
        // Fill with random positions and velocities
        for (let i = 0; i < count * 4; i++) {
            imgData.data[i] = Math.random() * 255;
        }
        
        ctx.putImageData(imgData, 0, 0);
        const texture = new THREE.CanvasTexture(canvas);
        
        // Create geometry and material
        const geometry = new THREE.BufferGeometry();
        // ... particle setup
    }
}

// Usage
const particleSystem = new GPUParticleSystem(scene, 50000);
```

## Performance Tips

1. **Adjust particle count based on device:**
```javascript
const particleCount = 
    navigator.deviceMemory >= 8 ? 15000 :
    navigator.deviceMemory >= 4 ? 8000 :
    4000;
```

2. **Use PixelRatio detection:**
```javascript
const pixelRatio = Math.min(window.devicePixelRatio, 2);
renderer.setPixelRatio(pixelRatio);
```

3. **Implement LOD (Level of Detail):**
```javascript
function updateLOD() {
    const distance = camera.position.distanceTo(particles.position);
    particles.material.size = distance > 100 ? 0.5 : 1.0;
}
```

## Integration with voidOS

Start system with particles:
```bash
python3 voidos_sentience.py
```

Access dashboard:
```
http://localhost:5001
```

Switch effects using buttons or API:
```javascript
// From console
switchParticleEffect('explosion')
```

---

**All examples use Three.js r128 from CDN - no build step required!**
