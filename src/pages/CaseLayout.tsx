import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import SiteNav, { SiteFooter } from "./SiteChrome";
import { CASESTUDIES } from "./catalogue";
import "./casestudy_toc.css";

// Shared case study page: contents list on the left (built from the h2 and h3 headings),
// the report in the centre and the other case studies on the right, underlined.

type Item = { id: string; label: string; sub: boolean };

const slugify = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export function Facts({ rows }: { rows: [string, string][] }) {
  return (
    <dl className="tc__facts">
      {rows.map(([k, v]) => [<dt key={k}>{k}</dt>, <dd key={k + "v"}>{v}</dd>])}
    </dl>
  );
}

export default function CaseLayout({ slug, children }: { slug: string; children: React.ReactNode }) {
  const main = useRef<HTMLElement>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [on, setOn] = useState("");

  // build the contents list from the headings and give each one an id
  useEffect(() => {
    const hs = Array.from(main.current?.querySelectorAll("h2, h3") ?? []) as HTMLElement[];
    const used = new Set<string>();
    const list = hs.map((h) => {
      let id = h.id || slugify(h.textContent || "s");
      while (used.has(id)) id += "-2";
      used.add(id); h.id = id;
      return { id, label: h.textContent || "", sub: h.tagName === "H3" };
    });
    setItems(list);
    const pick = () => {
      let cur = list[0]?.id ?? "";
      for (const it of list) { const el = document.getElementById(it.id); if (el && el.getBoundingClientRect().top < 140) cur = it.id; }
      setOn(cur);
    };
    pick();
    window.addEventListener("scroll", pick, { passive: true });
    return () => window.removeEventListener("scroll", pick);
  }, [slug]);

  const go = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    history.replaceState(null, "", `#${id}`);
  };
  const others = CASESTUDIES.filter((c) => c.slug !== slug);

  return (
    <>
      <SiteNav />
      <div className="tc">
        <nav className="tc__toc" aria-label="Contents">
          <p>Contents</p>
          <ol>
            {items.map(({ id, label, sub }) => (
              <li key={id} className={sub ? "s" : undefined}>
                <a href={`#${id}`} className={on === id ? "on" : undefined} onClick={(e) => go(e, id)}>{label}</a>
              </li>
            ))}
          </ol>
        </nav>

        <main className="tc__main" ref={main}>{children}</main>

        <aside className="tc__more" aria-label="Other case studies">
          <p>Other case studies</p>
          <ul>
            {others.map((c) => (
              <li key={c.slug}><Link to={`/case-studies/${c.slug}`}>{c.card ?? c.title}</Link></li>
            ))}
          </ul>
        </aside>
      </div>
      <SiteFooter />
    </>
  );
}
