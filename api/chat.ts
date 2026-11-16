// Vercel function: POST /api/chat  { messages: [{ role: "user" | "assistant", content: string }] } -> { reply: string }
// Free option: set GROQ_API_KEY (free at console.groq.com, no card). It picks the best available Groq model and moves to the next one when a model is busy; GROQ_MODEL puts a model first.
// Paid option, used only when GROQ_API_KEY is not set: ANTHROPIC_API_KEY, with CHAT_MODEL (default claude-opus-5-5).
import Anthropic from "@anthropic-ai/sdk";
import { KNOWLEDGE } from "./_knowledge.js";

const MODEL = process.env.CHAT_MODEL || "claude-opus-5-5";
const MAX_TURNS = 12;          // messages kept from the conversation
const MAX_CHARS = 1200;        // per visitor message

const SYSTEM = `You are a friendly, knowledgeable AI assistant on Kudzanai Chakavarika's GIS portfolio website. Visitors can ask you anything: about Kudzanai, about the maps and studies on the site, about GIS, remote sensing, mapping, data, coding, careers or any general topic. Answer every question helpfully and naturally, the way a capable general assistant would.

Guidance:
- For questions about Kudzanai (background, skills, experience, education, availability, projects), use the facts below. Do not invent facts about Kudzanai, such as employers, dates, prices or results that are not listed. If a detail about Kudzanai is not covered, say so and suggest emailing them.
- For everything else, answer from your own general knowledge. Where it fits naturally, you may point to related work on the site, but don't force it.
- When you mention a piece of work on the site, give its link exactly as written below (a path such as /case-studies/lake-kariba).
- Refer to Kudzanai by name or with they/them.
- Be clear and reasonably concise; match the length to the question. Plain text with short lists is fine; avoid headings and tables.
- Do not share a phone number or home address. For contact, give the email, LinkedIn or the CV link.

# Facts
${KNOWLEDGE}`;


type Msg = { role: "user" | "assistant"; content: string };

function clean(body: unknown): Msg[] | null {
  const raw = (body as { messages?: unknown })?.messages;
  if (!Array.isArray(raw)) return null;
  const msgs = raw
    .filter((m): m is Msg => !!m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string" && m.content.trim() !== "")
    .map((m) => ({ role: m.role, content: m.content.slice(0, MAX_CHARS) }))
    .slice(-MAX_TURNS);
  while (msgs.length && msgs[0].role !== "user") msgs.shift();      // must start with a user turn
  if (!msgs.length || msgs[msgs.length - 1].role !== "user") return null;
  return msgs;
}

const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

const NO_ANSWER = "Sorry, I don't have an answer for that. You can email Kudzanai at kudzanaichakavarika67@gmail.com.";

/* Groq: free tier, OpenAI-style chat completions endpoint.
   Each free model has its own per-minute token limit, so when one is busy (429) or retired, try the next. */
const GROQ = "https://api.groq.com/openai/v1";
const PREFS = [/gpt-oss-120b/i, /llama-3\.3-70b/i, /llama-4-maverick/i, /llama-4-scout/i, /qwen/i, /kimi/i, /gpt-oss-20b/i, /llama-3\.1-8b/i, /llama/i];
let models: string[] | null = null;     // cached list, best first
let lastGood = 0;                       // index of the model that last answered

async function groqModels(): Promise<string[]> {
  if (models) return models;
  let ids: string[] = [];
  try {
    const r = await fetch(`${GROQ}/models`, { headers: { authorization: `Bearer ${process.env.GROQ_API_KEY}` } });
    if (r.ok) ids = ((await r.json()) as { data?: { id: string; active?: boolean }[] }).data
      ?.filter((m) => m.active !== false).map((m) => m.id)
      .filter((id) => !/whisper|tts|guard|embed|vision|audio|compound|orpheus|playai/i.test(id)) ?? [];
  } catch { /* use the fallback below */ }
  const ranked: string[] = [];
  if (process.env.GROQ_MODEL) ranked.push(process.env.GROQ_MODEL);
  for (const p of PREFS) for (const id of ids) if (p.test(id) && !ranked.includes(id)) ranked.push(id);
  models = ranked.length ? ranked.slice(0, 5) : ["openai/gpt-oss-120b"];
  return models;
}

function callGroq(model: string, msgs: Msg[]) {
  return fetch(`${GROQ}/chat/completions`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${process.env.GROQ_API_KEY}` },
    body: JSON.stringify({
      model, max_tokens: 900, temperature: 0.5,
      ...(/gpt-oss/i.test(model) ? { reasoning_effort: "low", include_reasoning: false } : {}),
      messages: [{ role: "system", content: SYSTEM }, ...msgs],
    }),
  });
}

const DEV = process.env.NODE_ENV !== "production";

async function groq(msgs: Msg[]): Promise<Response> {
  const list = await groqModels();
  let status = 502, detail = "";
  for (let k = 0; k < list.length; k++) {
    const i = (lastGood + k) % list.length;
    const r = await callGroq(list[i], msgs);
    if (r.ok) {
      lastGood = i;
      const data = await r.json() as { choices?: { message?: { content?: string } }[] };
      return json({ reply: data.choices?.[0]?.message?.content?.trim() || NO_ANSWER, ...(DEV ? { model: list[i] } : {}) });
    }
    status = r.status; detail = (await r.text()).slice(0, 300);
    console.warn("groq", list[i], r.status, detail);
    if (r.status === 401) break;        // bad key: no point trying other models
  }
  return json({ error: status === 429 ? "busy" : "upstream", ...(DEV ? { status, detail } : {}) }, status === 429 ? 429 : 502);
}

export async function POST(req: Request): Promise<Response> {
  const useGroq = !!process.env.GROQ_API_KEY;
  if (!useGroq && !process.env.ANTHROPIC_API_KEY) return json({ error: "not_configured" }, 503);
  let msgs: Msg[] | null = null;
  try { msgs = clean(await req.json()); } catch { /* bad JSON */ }
  if (!msgs) return json({ error: "bad_request" }, 400);

  if (useGroq) {
    try { return await groq(msgs); } catch (err) { console.error(err); return json({ error: "server" }, 500); }
  }

  try {
    const client = new Anthropic();
    const res = await client.messages.create({
      model: MODEL,
      max_tokens: 2000,
      ...(MODEL.startsWith("claude-opus") ? { output_config: { effort: "low" as const } } : {}),
      system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],
      messages: msgs,
    });
    if (res.stop_reason === "refusal") return json({ reply: "Sorry, I can't help with that one. Try asking another way." });
    const reply = res.content.map((b) => (b.type === "text" ? b.text : "")).join("").trim();
    return json({ reply: reply || NO_ANSWER });
  } catch (err) {
    if (err instanceof Anthropic.RateLimitError) return json({ error: "busy" }, 429);
    if (err instanceof Anthropic.APIError) { console.error("claude", err.status, err.message); return json({ error: "upstream" }, 502); }
    console.error(err);
    return json({ error: "server" }, 500);
  }
}
