import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

const HeaderNav = () => {
  const [user, setUser] = useState(null);
  const [datetime, setDatetime] = useState(new Date());

  const location = useLocation();

  const isBackOffice =
    location.pathname.startsWith("/back_office")


  useEffect(() => {
    fetch("/api/profile")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setUser(data))
      .catch(() => setUser(null));
  }, []);

  useEffect(() => {
    const timer = setInterval(() => setDatetime(new Date()), 10000);
    return () => clearInterval(timer);
  }, []);

  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      await fetch("/api/logout-app", { method: "POST" });
    } catch (err) {
      console.error("logout-app failed:", err);
    }
    window.location.href = "/logout_app";
  };

  return (
    <header className="shadow-sm w-100" style={{
        backgroundColor: isBackOffice ? "#6189FF" : "#FF5F0D" }}>
      <div className="container-fluid py-3 d-flex align-items-center justify-content-between">
        <div className="d-flex align-items-center">
          <img 
            src="../static/tiger.ico"
            alt="Tiger logo"
            style={{ height: "44px", width: "44px", marginRight: "10px" }}
          />
          <a href="/" className="fw-bold fs-3 text-dark text-decoration-none">
            {isBackOffice ? "TigerBites Back Office" : "TigerBites" }
          </a>
        </div>

        <div className="d-flex align-items-center">
          <ul className="navbar-nav d-flex flex-row align-items-center">
            <li className="nav-item mx-3">
              <a className="nav-link text-dark fw-semibold" href="/discover">
                Discover
              </a>
            </li>
            <li className="nav-item mx-3">
              <a className="nav-link text-dark fw-semibold" href="/map">
                Map
              </a>
            </li>
            <li className="nav-item mx-3">
              <a className="nav-link text-dark fw-semibold" href="/group">
                Groups
              </a>
            </li>
            <li className="nav-item mx-3">
              <a className="nav-link text-light fw-semibold" href="/profile">
                Profile
              </a>
            </li>
            <li className="nav-item mx-3">
              <a
                className="nav-link text-light fw-semibold"
                href="#"
                onClick={handleLogout}
              >
                Logout
              </a>
            </li>
          </ul>

          <div className="text-end me-4">
            {user ? (
              <div className="fw-semibold text-dark">
                Welcome, {user.firstname || user.username || "Guest"}!
              </div>
            ) : (
              <div className="text-muted fst-italic">Welcome, Guest!</div>
            )}
            <div className="text-dark small">
              {datetime.toLocaleString("en-US", {
                weekday: "short",
                hour: "numeric",
                minute: "2-digit",
              })}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default HeaderNav;
