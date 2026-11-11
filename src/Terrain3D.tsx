import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

/* Real-time 3D terrain "video". If /videos/3d-terrain.mp4 exists in /public it plays instead. */
const VIDEO_SRC = "/videos/3d-terrain.mp4";

function hash(x: number, y: number) {
  const s = Math.sin(x * 127.1 + y * 311.7) * 43758.5453;
  return s - Math.floor(s);
}
function vnoise(x: number, y: number) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  return (
    hash(xi, yi) * (1 - u) * (1 - v) + hash(xi + 1, yi) * u * (1 - v) +
    hash(xi, yi + 1) * (1 - u) * v + hash(xi + 1, yi + 1) * u * v
  );
}
function fbm(x: number, y: number) {
  let a = 0.5, f = 1, t = 0;
  for (let i = 0; i < 6; i++) {
    t += a * (1 - Math.abs(vnoise(x * f, y * f) * 2 - 1)); // ridged = sharp peaks
    f *= 2; a *= 0.5;
  }
  return t;
}
const RAMP: [number, number[]][] = [
  [0.0, [0.1, 0.25, 0.85]], [0.18, [0.1, 0.55, 0.9]], [0.3, [0.1, 0.65, 0.2]],
  [0.55, [0.65, 0.85, 0.1]], [0.75, [0.98, 0.8, 0.1]], [1.0, [0.95, 0.3, 0.05]],
];
function ramp(t: number) {
  for (let i = 1; i < RAMP.length; i++) {
    if (t <= RAMP[i][0]) {
      const [t0, c0] = RAMP[i - 1], [t1, c1] = RAMP[i];
      const k = (t - t0) / (t1 - t0);
      return c0.map((v, j) => v + (c1[j] - v) * k);
    }
  }
  return RAMP[RAMP.length - 1][1];
}

export default function Terrain3D({ className = "" }: { className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [hasVideo, setHasVideo] = useState<boolean | null>(null);

  useEffect(() => {
    fetch(VIDEO_SRC, { method: "HEAD" })
      .then(r => setHasVideo(r.ok && (r.headers.get("content-type") || "").includes("video")))
      .catch(() => setHasVideo(false));
  }, []);

  useEffect(() => {
    if (hasVideo !== false || !ref.current) return;
    const el = ref.current;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    el.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x0b1210, 40, 95);
    const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 200);

    const N = 160, SIZE = 60;
    const geo = new THREE.PlaneGeometry(SIZE, SIZE, N, N);
    geo.rotateX(-Math.PI / 2);
    const pos = geo.attributes.position as THREE.BufferAttribute;
    const col = new Float32Array(pos.count * 3);
    const hs: number[] = [];
    let min = Infinity, max = -Infinity;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), z = pos.getZ(i);
      const d = Math.hypot(x, z) / (SIZE / 2);
      const h = fbm(x * 0.045 + 3, z * 0.045 + 7) * (1 - Math.pow(d, 3) * 0.9);
      hs.push(h); min = Math.min(min, h); max = Math.max(max, h);
    }
    for (let i = 0; i < pos.count; i++) {
      const t = (hs[i] - min) / (max - min);
      pos.setY(i, Math.pow(t, 1.4) * 15 - 2);
      const c = ramp(t);
      col.set(c, i * 3);
    }
    geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
    geo.computeVertexNormals();
    const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9, metalness: 0 }));
    scene.add(mesh);
    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const sun = new THREE.DirectionalLight(0xfff1d6, 1.6);
    sun.position.set(30, 28, 12);
    scene.add(sun);

    const resize = () => {
      const w = el.clientWidth || 1, h = el.clientHeight || 1;
      renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
    };
    resize();
    const ro = new ResizeObserver(resize); ro.observe(el);

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let raf = 0, visible = true;
    const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; }, { threshold: 0 });
    io.observe(el);
    const t0 = performance.now();
    const loop = () => {
      raf = requestAnimationFrame(loop);
      if (!visible) return;
      const t = reduce ? 0 : (performance.now() - t0) / 1000;
      const a = t * 0.12;
      camera.position.set(Math.sin(a) * 46, 22 + Math.sin(t * 0.3) * 3, Math.cos(a) * 46);
      camera.lookAt(0, 4, 0);
      renderer.render(scene, camera);
    };
    loop();
    return () => {
      cancelAnimationFrame(raf); ro.disconnect(); io.disconnect();
      geo.dispose(); (mesh.material as THREE.Material).dispose(); renderer.dispose();
      if (renderer.domElement.parentNode === el) el.removeChild(renderer.domElement);
    };
  }, [hasVideo]);

  if (hasVideo) {
    return <video className={className} src={VIDEO_SRC} autoPlay loop muted playsInline style={{ width: "100%", height: "100%", objectFit: "cover" }} />;
  }
  return <div ref={ref} className={className} style={{ width: "100%", height: "100%" }} aria-label="Animated 3D terrain model" role="img" />;
}
