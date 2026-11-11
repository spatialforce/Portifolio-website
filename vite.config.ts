import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

/* The Event Gallery is a separate app, built into public/event-gallery (npm run gallery).
   It asks for its data at /data/..., and its own pages live under /event-gallery/... */
function eventGallery(): Plugin {
  const route = (req: { url?: string }, _res: unknown, next: () => void) => {
    const url = req.url || "";
    if (url.startsWith("/data/")) req.url = "/event-gallery" + url;
    else if (url.startsWith("/event-gallery") && !/\.[a-z0-9]+(\?|$)/i.test(url)) req.url = "/event-gallery/index.html";
    next();
  };
  return {
    name: "event-gallery",
    configureServer: (s) => { s.middlewares.use(route); },
    configurePreviewServer: (s) => { s.middlewares.use(route); },
  };
}

// GitHub Pages serves the site from /Portifolio-website/, set through PAGES_BASE in the Pages workflow
export default defineConfig({ base: process.env.PAGES_BASE || "/", plugins: [eventGallery(), react()] });
