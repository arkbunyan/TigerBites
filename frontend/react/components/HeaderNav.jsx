import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import TutorialModal from "./TutorialModal.jsx";

const HeaderNav = () => {
  const [user, setUser] = useState(null);
  const [datetime, setDatetime] = useState(new Date());
  const [showTutorial, setShowTutorial] = useState(false);

  const location = useLocation();

  const isBackOffice =
    location.pathname.startsWith("/back_office")

  // Hide the global header on the homepage for a clean landing experience
  const hideOnHome = location.pathname === "/";


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

  // Show tutorial for first-time users only after login
  useEffect(() => {
    try {
      const seen = localStorage.getItem("tb_seen_tutorial");
      // Only show if not seen AND user is authenticated
      if (!seen && user && (user.username || user.firstname)) {
        setShowTutorial(true);
      }
    } catch {}
  }, [user]);

  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      await fetch("/api/logout-app", { method: "POST" });
    } catch (err) {
      console.error("logout-app failed:", err);
    }
    window.location.href = "/logout_app";
  };

  if (hideOnHome) {
    return <TutorialModal open={showTutorial} onClose={() => setShowTutorial(false)} />;
  }

  return (
    <>
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
              <a className="nav-link text-dark fw-semibold" href={isBackOffice ?  "/back_office" :  "/discover" }>
                Discover
              </a>
            </li>
            <li className="nav-item mx-3">
              <a className="nav-link text-dark fw-semibold" href={isBackOffice ? "/back_office/feedback" : "/map" }>
                {isBackOffice ? "Feedback" : "Map" }
              </a>
            </li>
            <li className="nav-item mx-3">
              <a className="nav-link text-dark fw-semibold" href={isBackOffice ? "/back_office/reviews": "/group"}>
                {isBackOffice ? "Reviews" : "Groups"}
              </a>
            </li>
            <li className="nav-item mx-3">
              <a className="nav-link text-dark fw-semibold" href="/profile">
                Profile
              </a>
            </li>
            <li className="nav-item mx-3">
              <a
                className="nav-link text-dark fw-semibold"
                href="#"
                onClick={(e) => { e.preventDefault(); setShowTutorial(true); }}
              >
                Help
              </a>
            </li>
            <li className="nav-item mx-3">
                <a
                  className="nav-link text-light fw-semibold"
                  href={
                    isBackOffice
                      ? (user?.admin_status ? "/discover" : "#")
                      : "/back_office"
                  }
                  style={{
                    pointerEvents: user?.admin_status ? "auto" : "none",
                    opacity: user?.admin_status ? 1 : 0.5
                  }}
                >
                  {isBackOffice ? "Exit Back Office" : "Admin"}
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
    <TutorialModal open={showTutorial} onClose={() => setShowTutorial(false)} />
    </>
  );
};

export default HeaderNav;
