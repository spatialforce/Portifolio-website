import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { CASESTUDIES, WEBMAPS, STORYMAPS, DASHBOARDS } from "../pages/catalogue";
import { EMAIL } from "../pages/SiteChrome";
import "./chat.css";

type Msg = { role: "user" | "assistant"; content: string };

const HELLO = "Hi, I'm an AI assistant. Ask me anything: about Kudzanai and the work on this site, GIS and remote sensing, or any other topic.";
const CHIPS = ["Tell me about Kudzanai", "Which projects use satellite imagery?", "What is AHP in GIS?", "How can I contact Kudzanai?"];

/* site items, used to show page names for links in answers */
const ITEMS = [
  ...CASESTUDIES.map((p) => ({ title: p.card || p.title, words: `${p.title} ${p.sub ?? ""} ${p.text} ${p.place ?? ""}`, href: `/case-studies/${p.slug}` })),
  ...WEBMAPS.map((m) => ({ title: m.title, words: `${m.title} ${m.short} ${m.text} ${m.stack.join(" ")}`, href: `/maps/${m.slug}` })),
  ...STORYMAPS.map((s) => ({ title: s.title, words: `${s.title} ${s.text} ${s.stack.join(" ")}`, href: `/stories/${s.slug}` })),
  ...DASHBOARDS.map((d) => ({ title: d.title, words: `${d.title} ${d.text} ${d.stack.join(" ")}`, href: `/dashboards/${d.slug}` })),
];
const OFFLINE = `The AI assistant can't be reached right now. Please try again in a moment, or email Kudzanai directly at ${EMAIL}.`;
const BUSY = "Lots of questions right now. Please try again in a few seconds.";

/* ---------------- render text with links ---------------- */
const TOKEN = /(https?:\/\/[^\s)]+|\/(?:case-studies|maps|stories|dashboards|projects)[\w\-/]*|\/#\w+|\/Kudzanai_Chakavarika_CV\.pdf|[\w.+-]+@[\w-]+\.[\w.]+)/g;
function bold(text: string, k: number): ReactNode[] {
  return text.split(/\*\*(.+?)\*\*/g).map((t, j) => (j % 2 ? <strong key={`${k}-${j}`}>{t}</strong> : t));
}
function rich(text: string, close: () => void): ReactNode[] {
  return text.split(TOKEN).map((part, i) => {
    if (i % 2 === 0) return <span key={i}>{bold(part, i)}</span>;
    const p = part.replace(/[.,;:]+$/, "");
    const tail = part.slice(p.length);
    if (p.includes("@")) return <span key={i}><a href={`mailto:${p}`}>{p}</a>{tail}</span>;
    if (p.startsWith("http") || p.endsWith(".pdf")) return <span key={i}><a href={p} target="_blank" rel="noreferrer">{p.replace(/^https?:\/\/(www\.)?/, "")}</a>{tail}</span>;
    const name = ITEMS.find((it) => it.href === p)?.title;
    return <span key={i}><Link to={p} onClick={close}>{name ?? p}</Link>{tail}</span>;
  });
}

export default function ChatBot() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { end.current?.scrollIntoView({ block: "end" }); }, [msgs, busy]);
  useEffect(() => { if (open) input.current?.focus(); }, [open]);
  useEffect(() => {
    const f = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, []);

  async function ask(q: string) {
    q = q.trim();
    if (!q || busy) return;
    const next: Msg[] = [...msgs, { role: "user", content: q }];
    setMsgs(next); setText(""); setBusy(true);
    let reply = OFFLINE;
    const send = () => fetch("/api/chat", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ messages: next }) });
    try {
      let r = await send();
      if (r.status === 429) { await new Promise((ok) => setTimeout(ok, 9000)); r = await send(); }   // free tier is busy: wait, then retry once
      if (r.ok) reply = (await r.json()).reply || OFFLINE;
      else if (r.status === 429) reply = BUSY;
    } catch { /* network error: keep OFFLINE */ }
    setMsgs([...next, { role: "assistant", content: reply }]);
    setBusy(false);
  }

  const close = () => setOpen(false);

  return (
    <>
      <button className={`chat__fab ${open ? "chat__fab--hide" : ""}`} onClick={() => setOpen(true)} aria-label="Ask a question about Kudzanai">
        <i className="bi bi-chat-text" aria-hidden="true" /> Ask me
      </button>
      {open && (
        <section className="chat" role="dialog" aria-label="Questions about Kudzanai">
          <header className="chat__head">
            <span>Ask about Kudzanai</span>
            <button onClick={close} aria-label="Close"><i className="bi bi-x-lg" aria-hidden="true" /></button>
          </header>
          <div className="chat__log" aria-live="polite">
            <p className="chat__msg chat__msg--bot">{HELLO}</p>
            {msgs.length === 0 && (
              <div className="chat__chips">{CHIPS.map((c) => <button key={c} onClick={() => ask(c)}>{c}</button>)}</div>
            )}
            {msgs.map((m, i) => (
              <p key={i} className={`chat__msg ${m.role === "user" ? "chat__msg--me" : "chat__msg--bot"}`}>
                {m.role === "user" ? m.content : rich(m.content, close)}
              </p>
            ))}
            {busy && <p className="chat__msg chat__msg--bot chat__dots"><span /><span /><span /></p>}
            <div ref={end} />
          </div>
          <form className="chat__form" onSubmit={(e) => { e.preventDefault(); ask(text); }}>
            <textarea ref={input} rows={1} value={text} maxLength={1200} placeholder="Type a question" onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(text); } }} />
            <button type="submit" disabled={busy || !text.trim()} aria-label="Send"><i className="bi bi-send" aria-hidden="true" /></button>
          </form>
        </section>
      )}
    </>
  );
}
