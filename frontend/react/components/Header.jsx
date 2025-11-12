import React, { useState, useEffect } from "react";

const Header = () => {
  const [user, setUser] = useState(null);
  const [datetime, setDatetime] = useState(new Date());

  // Fetch user info on component mount
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

  const greeting = "TigerBites";

  return (
    <header
      className="py-4 mb-3 shadow-sm border-bottom"
      style={{
        backgroundColor: "#FF5F0D",
      }}
    >
      <div className="container d-flex flex-column flex-md-row justify-content-between align-items-center">
        <h1 className="display-5 fw-bold text-dark mb-2 mb-md-0">{greeting}</h1>

        <div className="text-end">
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
    </header>
  );
};

export default Header;
