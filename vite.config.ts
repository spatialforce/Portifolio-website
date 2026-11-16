import { defineConfig, loadEnv, type Plugin } from "vite";
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

/* Local testing of the Vercel function: npm run dev serves POST /api/chat from api/chat.ts.
   Put GROQ_API_KEY=... in .env.local (git-ignored) for this to work on your computer. */
function apiDev(): Plugin {
  return {
    name: "api-dev",
    configureServer(server) {
      Object.assign(process.env, loadEnv(server.config.mode, process.cwd(), ""));
      server.middlewares.use("/api/chat", async (req, res) => {
        try {
          const chunks: Buffer[] = [];
          for await (const c of req) chunks.push(c as Buffer);
          const mod = await server.ssrLoadModule("/api/chat.ts");
          const r: Response = await mod.POST(new Request("http://localhost/api/chat", { method: req.method, headers: { "content-type": "application/json" }, body: req.method === "POST" ? Buffer.concat(chunks) : undefined }));
          res.statusCode = r.status;
          res.setHeader("content-type", "application/json");
          res.end(await r.text());
        } catch (e) { console.error(e); res.statusCode = 500; res.end('{"error":"server"}'); }
      });
    },
  };
}

// GitHub Pages serves the site from /Portifolio-website/, set through PAGES_BASE in the Pages workflow
export default defineConfig({ base: process.env.PAGES_BASE || "/", plugins: [apiDev(), eventGallery(), react()] });
