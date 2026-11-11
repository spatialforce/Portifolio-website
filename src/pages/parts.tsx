import type { ReactNode } from "react";

/* A map image with an optional caption underneath. Clicking opens the full-size file. */
export function Figure({ src, alt, name, children }: { src: string; alt: string; name?: string; children?: ReactNode }) {
  return (
    <figure className="fig">
      <a className="fig__img" href={src} target="_blank" rel="noopener noreferrer" title="Open full size">
        <img src={src} alt={alt} loading="lazy" />
      </a>
      {(name || children) && (
        <figcaption>
          {name && <b>{name}</b>}
          {name && children ? " " : null}
          {children}
        </figcaption>
      )}
    </figure>
  );
}

/* A short row of headline numbers. */
export function Stats({ items }: { items: { value: string; label: string }[] }) {
  return (
    <div className="stats">
      {items.map((s) => (
        <div key={s.label} className="stats__item">
          <span className="stats__value">{s.value}</span>
          <span className="stats__label">{s.label}</span>
        </div>
      ))}
    </div>
  );
}

/* Contact block that closes each project page. */
export function ProjectContact({ children }: { children: ReactNode }) {
  return (
    <section className="psection pcta">
      <h2 className="sec-h">Want the full data?</h2>
      <p>{children}</p>
      <div className="pcta__actions">
        <a href="mailto:kudzanaichakavarika67@gmail.com" className="btn">Email me</a>
        <a href="/cv.pdf" target="_blank" rel="noreferrer" className="btn btn--line">Download CV</a>
      </div>
    </section>
  );
}
