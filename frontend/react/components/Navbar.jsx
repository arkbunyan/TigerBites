import React from "react";

const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light px-3">
      <a className="navbar-brand" href="/">
        Tiger Bites
      </a>
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>

      <div className="collapse navbar-collapse" id="navbarNav">
        <ul className="navbar-nav ms-auto">
          <li className="nav-item me-3">
            <a className="nav-link" href="/home">
              Discover
            </a>
          </li>
          <li className="nav-item me-3">
            <a className="nav-link" href="/map_page">
              Map
            </a>
          </li>
          <li className="nav-item me-3">
            <a className="nav-link" href="/">
              Groups
            </a>
          </li>
          <li className="nav-item me-3">
            <a className="nav-link" href="/profile_page">
              Profile
            </a>
          </li>
          <li className="nav-item me-3">
            <a className="nav-link" href="/logout_app">
              Logout of TigerBites
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="/logout_cas">
              Logout of CAS
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
