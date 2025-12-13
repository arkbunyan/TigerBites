import React, { useState } from "react";

const HomePage = () => {
  const [hover, setHover] = useState(false);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(180deg, #ff8f59 0%, #ff8a4a 40%, #ff7a3a 100%)",
      }}
    >
      <div className="text-center" style={{ maxWidth: 920, padding: "48px 24px" }}>
        {/* Logo */}
        <div className="mb-3" style={{ display: "flex", justifyContent: "center" }}>
          <img
            src="../../static/tiger.ico"
            alt="Tiger logo"
            style={{ width: 96, height: 96, borderRadius: 6 }}
          />
        </div>

        {/* Title */}
        <h1 className="fw-bold" style={{ fontSize: 56, color: "#fffefc", margin: "8px 0 6px 0" }}>
          TigerBites
        </h1>

        {/* Lead paragraph */}
        <p className="lead" style={{ fontSize: 18, color: "rgba(255,255,255,0.95)", margin: "12px 0 18px 0" }}>
          Discover the perfect place to eat at Princeton. Find restaurants, explore menus, read reviews, and connect with friends.
        </p>

        {/* Supporting paragraph */}
        <p style={{ fontSize: "14.5px", color: "rgba(255,255,255,0.9)", margin: "16px 0 22px 0", lineHeight: 1.7 }}>
          Update your preferences in your profile, create groups with friends, get personalized recommendations, and explore restaurants on our map. Find what satisfies your cravings instantly.
        </p>

        {/* Get Started Button */}
        <div style={{ marginTop: 28 }}>
          <a href="/discover" className="text-decoration-none">
            <button
              className="btn btn-light fw-bold"
              style={{
                fontSize: 16,
                color: "#ff7a2d",
                borderRadius: 999,
                padding: "14px 38px",
                boxShadow: hover ? "0 18px 48px rgba(0,0,0,0.18)" : "0 10px 30px rgba(0,0,0,0.12)",
                transform: hover ? "translateY(-4px)" : "translateY(0)",
                transition: "transform 160ms ease, box-shadow 160ms ease",
                border: "none",
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
              }}
              onMouseEnter={() => setHover(true)}
              onMouseLeave={() => setHover(false)}
              aria-label="Get started with TigerBites"
            >
              <span>Get Started</span>
              <span style={{ marginLeft: 10, fontWeight: 800 }}>→</span>
            </button>
          </a>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
