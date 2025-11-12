import React from "react";

const Navbar = () => {
  const handleLogoutApp = async (e) => {
    e?.preventDefault();
    try {
      await fetch("/api/logout-app", { method: "POST" });
    } catch (err) {
      console.error("logout-app failed:", err);
    }
    window.location.href = "/logout_app";
  };

  const handleLogoutCas = (e) => {
    e?.preventDefault();
    window.location.href = "/logoutcas";
  };

  return (
    <nav
      className="navbar shadow-sm px-4"
      style={{
        backgroundColor: "#FF5F0D",
      }}
    >
      <div className="container-fluid d-flex justify-content-between align-items-center">
        <a className="navbar-brand fw-bold text-dark fs-4" href="/">
          🍴 TigerBites
        </a>
        <ul className="navbar-nav d-flex flex-row mb-0 align-items-center">
          <li className="nav-item mx-2">
            <a className="nav-link text-dark fw-semibold" href="/">
              Discover
            </a>
          </li>
          <li className="nav-item mx-2">
            <a className="nav-link text-dark fw-semibold" href="/map_page">
              Map
            </a>
          </li>
          <li className="nav-item mx-2">
            <a className="nav-link text-dark fw-semibold" href="/">
              Groups
            </a>
          </li>
          <li className="nav-item mx-2">
            <a className="nav-link text-dark fw-semibold" href="/profile">
              Profile
            </a>
          </li>
          <li className="nav-item mx-2">
            <a
              className="nav-link text-light fw-semibold"
              href="#"
              onClick={handleLogoutApp}
            >
              Logout of TigerBites
            </a>
          </li>
          <li className="nav-item mx-2">
            <a
              className="nav-link text-light fw-semibold"
              href="#"
              onClick={handleLogoutCas}
            >
              Logout of CAS
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
