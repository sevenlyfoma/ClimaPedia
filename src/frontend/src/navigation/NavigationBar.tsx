// Using a Bootstrap navigation bar, which can be found here:
// https://getbootstrap.com/docs/5.3/components/navbar/#how-it-works

import "../App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import { SetStateAction } from "react";
import { NavLink } from "react-router-dom";

// Nav bar
function NavigationBar({
  setShowSettings,
}: {
  showSettings: boolean;
  setShowSettings: React.Dispatch<SetStateAction<boolean>>;
}) {
  return (
    <nav className="navbar navbar-expand-sm bg-body-tertiary">
      <div className="container-fluid">
        <a
          className="navbar-brand ms-1 d-flex gap-3 align-items-center fw-bold"
          href="/"
        >
          <img
            src="logo.svg"
            alt="The WeatherWiki logo: a stylized cloud containing a network of interconnected points"
            height={32}
          />
          WeatherWiki
        </a>
        <div className="d-flex">
          <button
            className="navbar-toggler border-0"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="material-symbols-outlined text-dark">menu</span>
          </button>
          <button
            className="nav-link ms-3 me-1 d-sm-none"
            onClick={() => setShowSettings((v) => !v)}
            role="button"
          >
            <span className="material-symbols-outlined text-dark">
              settings
            </span>
          </button>
        </div>
        <div
          className="collapse navbar-collapse justify-content-between"
          id="navbarSupportedContent"
        >
          <ul className="navbar-nav ms-auto align-items-sm-center ps-1">
            <li className="nav-item text-start">
              <NavLink to="/" className="nav-link">
                Map
              </NavLink>
            </li>
            <li className="nav-item text-start">
              <NavLink to="/chart" className="nav-link">
                Chart
              </NavLink>
            </li>
            <li className="nav-item text-start">
              <NavLink to="/timeline" className="nav-link">
                Timeline
              </NavLink>
            </li>
            <button
              className="nav-link ms-3 me-1 d-none d-sm-block"
              onClick={() => setShowSettings((v) => !v)}
              role="button"
            >
              <span className="material-symbols-outlined">settings</span>
            </button>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default NavigationBar;
