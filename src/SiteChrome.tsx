import { Link } from "react-router-dom";

export default function SiteNav() {
  return (
    <nav className="snav">
      <Link to="/" className="snav__brand">Kudzanai Chakavarika</Link>
      <div className="snav__links">
        <Link to="/">HOME</Link>
        <Link to="/projects">PORTFOLIO</Link>
        <a href="/#contact">CONTACT</a>
      </div>
    </nav>
  );
}

export function SiteFooter() {
  return (
    <footer className="sfoot">
      <p>Want to talk about a project? <a href="mailto:kudzanaichakavarika67@gmail.com">kudzanaichakavarika67@gmail.com</a></p>
      <small>© {new Date().getFullYear()}, Kudzanai Chakavarika</small>
    </footer>
  );
}
