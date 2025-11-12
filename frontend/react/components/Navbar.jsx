import React from "react";

const Navbar = () => {
  const handleLogoutApp = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    try {
      await fetch("/api/logout-app", { method: "POST" });
    } catch (err) {
      // ignore network errors but still redirect to logout page
      console.error("logout-app failed:", err);
    }
    window.location.href = "/logout_app";
  };

  const handleLogoutCas = (e) => {
    if (e && e.preventDefault) e.preventDefault();
    window.location.href = "/logoutcas";
  };

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
            <a className="nav-link" href="/">
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
            <a className="nav-link" href="/profile">
              Profile
            </a>
          </li>
          <li className="nav-item me-3">
            <a className="nav-link" href="#" onClick={handleLogoutApp}>
              Logout of TigerBites
            </a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#" onClick={handleLogoutCas}>
              Logout of CAS
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
