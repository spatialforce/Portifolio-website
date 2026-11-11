import { useEffect, useRef } from "react";
import * as THREE from "three";
import demUrl from "../assets/chimanimani_dem.png";

/* Chimanimani mountains, eastern Zimbabwe, from real elevation (SRTM via AWS Terrain Tiles).
   The heightmap stores elevation in 16 bits: red = high byte, green = low byte. */
const BOX = { w: 32.7, e: 33.15, s: -20.05, n: -19.6 };
const LO = 209, HI = 2426; // metres, the range packed into the PNG
const BG = new THREE.Color("#0d1012");

const VERT = /* glsl */ `
  attribute float elev;
  varying float vElev;
  varying vec3 vNormal;
  varying vec2 vUv;
  varying float vDepth;
  void main() {
    vElev = elev;
    vNormal = normal;
    vUv = uv;
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    vDepth = -mv.z;
    gl_Position = projectionMatrix * mv;
  }
`;

const FRAG = /* glsl */ `
  uniform vec3 uSun;
  uniform vec3 uBg;
  uniform float uSweep;
  varying float vElev;
  varying vec3 vNormal;
  varying vec2 vUv;
  varying float vDepth;

  float line(float v, float w) {
    float f = abs(fract(v - 0.5) - 0.5);
    return 1.0 - smoothstep(0.0, fwidth(v) * w, f);
  }

  void main() {
    float t = clamp((vElev - ${LO.toFixed(1)}) / ${(HI - LO).toFixed(1)}, 0.0, 1.0);
    // earthy hypsometric tints: valley forest to bare quartzite
    vec3 c = mix(vec3(0.07, 0.11, 0.09), vec3(0.20, 0.25, 0.17), smoothstep(0.0, 0.35, t));
    c = mix(c, vec3(0.42, 0.40, 0.31), smoothstep(0.35, 0.75, t));
    c = mix(c, vec3(0.74, 0.71, 0.63), smoothstep(0.78, 1.0, t));

    float light = max(dot(normalize(vNormal), normalize(uSun)), 0.0);
    c *= 0.28 + 0.95 * light;

    // contours every 50 m, index contours every 250 m
    vec3 ink = vec3(0.95, 0.91, 0.82);
    c = mix(c, ink, line(vElev / 50.0, 1.0) * 0.16);
    c = mix(c, ink, line(vElev / 250.0, 1.4) * 0.42);

    // one contour climbing the mountains
    // two climbing contours, a third of the height range apart, so one is always on the slopes in view
    float range = ${(HI - LO - 300).toFixed(1)};
    float w = fwidth(vElev) * 1.8 + 1.5;
    float s1 = 1.0 - smoothstep(0.0, w, abs(vElev - uSweep));
    float e2 = uSweep - range / 3.0; if (e2 < ${(LO + 260).toFixed(1)}) e2 += range;
    float s2 = 1.0 - smoothstep(0.0, w, abs(vElev - e2));
    c = mix(c, vec3(0.93, 0.42, 0.20), max(s1, s2 * 0.75));

    // the tile fades into the night at its edges and in the distance
    vec2 e = smoothstep(vec2(0.0), vec2(0.16), vUv) * smoothstep(vec2(0.0), vec2(0.16), 1.0 - vUv);
    float fade = e.x * e.y * (1.0 - smoothstep(60.0, 120.0, vDepth));
    gl_FragColor = vec4(mix(uBg, c, fade), 1.0);
  }
`;

const nf = (v: number) => Math.round(v).toLocaleString("en-US").replace(/,/g, " ");

type Props = { className?: string; onSweep?: (m: string) => void; onProbe?: (s: string | null) => void };

export default function Terrain3D({ className = "", onSweep, onProbe }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const cb = useRef({ onSweep, onProbe });
  cb.current = { onSweep, onProbe };

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let disposed = false;
    let cleanup = () => {};

    const img = new Image();
    img.src = demUrl;
    img.onload = () => {
      if (disposed) return;
      const R = img.width;
      const cv = document.createElement("canvas");
      cv.width = cv.height = R;
      const cx = cv.getContext("2d", { willReadFrequently: true })!;
      cx.drawImage(img, 0, 0);
      const px = cx.getImageData(0, 0, R, R).data;
      const elev = new Float32Array(R * R);
      for (let i = 0; i < R * R; i++) elev[i] = LO + ((px[i * 4] * 256 + px[i * 4 + 1]) / 65535) * (HI - LO);

      const SIZE = 70, VZ = 0.0045; // 70 units = 47 km across, so heights are exaggerated about 3x
      const geo = new THREE.PlaneGeometry(SIZE, SIZE, R - 1, R - 1);
      geo.rotateX(-Math.PI / 2);
      const pos = geo.attributes.position as THREE.BufferAttribute;
      for (let i = 0; i < pos.count; i++) pos.setY(i, (elev[i] - LO) * VZ);
      geo.setAttribute("elev", new THREE.BufferAttribute(elev, 1));
      geo.computeVertexNormals();

      const mat = new THREE.ShaderMaterial({
        vertexShader: VERT,
        fragmentShader: FRAG,
        uniforms: {
          uSun: { value: new THREE.Vector3(-0.6, 0.75, -0.35) },
          uBg: { value: BG },
          uSweep: { value: LO },
        },
      });
      const mesh = new THREE.Mesh(geo, mat);

      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setClearColor(BG);
      el.appendChild(renderer.domElement);
      const scene = new THREE.Scene();
      scene.add(mesh);
      const camera = new THREE.PerspectiveCamera(38, 1, 0.5, 300);

      const resize = () => {
        const w = el.clientWidth || 1, h = el.clientHeight || 1;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      };
      resize();
      const ro = new ResizeObserver(resize);
      ro.observe(el);

      // pointer: gentle parallax, plus the elevation under the cursor
      const mouse = new THREE.Vector2(9, 9);
      const par = { x: 0, y: 0, tx: 0, ty: 0 };
      const ray = new THREE.Raycaster();
      let lastProbe = 0;
      const move = (e: PointerEvent) => {
        const r = el.getBoundingClientRect();
        if (e.clientY > r.bottom) { leave(); return; }
        mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
        par.tx = mouse.x; par.ty = mouse.y;
      };
      const leave = () => { mouse.set(9, 9); par.tx = par.ty = 0; cb.current.onProbe?.(null); };
      window.addEventListener("pointermove", move, { passive: true });

      const probe = () => {
        if (mouse.x > 1.5) return;
        ray.setFromCamera(mouse, camera);
        const hit = ray.intersectObject(mesh)[0];
        if (!hit || !hit.uv) { cb.current.onProbe?.(null); return; }
        const u = hit.uv.x, v = hit.uv.y;
        if (Math.min(u, v, 1 - u, 1 - v) < 0.06) { cb.current.onProbe?.(null); return; }
        const ix = Math.min(R - 1, Math.round(u * (R - 1))), iy = Math.min(R - 1, Math.round((1 - v) * (R - 1)));
        const lon = BOX.w + u * (BOX.e - BOX.w), lat = BOX.s + v * (BOX.n - BOX.s);
        cb.current.onProbe?.(`${Math.abs(lat).toFixed(3)}° S ${lon.toFixed(3)}° E. Elevation ${nf(elev[iy * R + ix])} m`);
      };

      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      let visible = true, raf = 0, lastLabel = "";
      const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; });
      io.observe(el);
      const t0 = performance.now();

      const loop = () => {
        raf = requestAnimationFrame(loop);
        if (!visible) return;
        const t = reduce ? 40 : (performance.now() - t0) / 1000;
        par.x += (par.tx - par.x) * 0.04;
        par.y += (par.ty - par.y) * 0.04;
        const a = 0.9 + t * 0.035 + par.x * 0.12;
        const narrow = camera.aspect < 1;
        const dist = narrow ? 62 : 56;
        camera.position.set(Math.sin(a) * dist, 27 + par.y * 3 + (narrow ? 10 : 0), Math.cos(a) * dist);
        // on wide screens the mountains sit right of centre, leaving the left for the text
        const off = narrow ? 0 : 9;
        camera.lookAt(-Math.cos(a) * off, 2, Math.sin(a) * off);

        // the orange contour climbs steadily through the mountains and starts again every 22 s.
        // It begins halfway up, where the terrain is in full view, so it shows from the first frame.
        const k = ((t + 9) % 22) / 22;
        const m = LO + 260 + (HI - LO - 300) * k;
        mat.uniforms.uSweep.value = m;
        const label = nf(Math.round(m / 10) * 10);
        if (label !== lastLabel) { lastLabel = label; cb.current.onSweep?.(label); }

        const now = performance.now();
        if (now - lastProbe > 90) { lastProbe = now; probe(); }
        renderer.render(scene, camera);
      };
      loop();

      cleanup = () => {
        cancelAnimationFrame(raf); ro.disconnect(); io.disconnect();
        window.removeEventListener("pointermove", move);
        geo.dispose(); mat.dispose(); renderer.dispose();
        if (renderer.domElement.parentNode === el) el.removeChild(renderer.domElement);
      };
    };

    return () => { disposed = true; cleanup(); };
  }, []);

  return <div ref={ref} className={className} style={{ width: "100%", height: "100%" }}
    role="img" aria-label="3D terrain of the Chimanimani mountains, eastern Zimbabwe, with contour lines" />;
}
