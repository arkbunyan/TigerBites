import React, { useState } from "react";
import "./HomePage.css";

const HomePage = () => {
  const [hover, setHover] = useState(false);

  const buttonBase = {
    borderRadius: 999,
    padding: "12px 36px",
    fontWeight: 800,
    fontSize: 16,
    border: "none",
    cursor: "pointer",
    transition: "transform 160ms ease, box-shadow 160ms ease",
  };

  const buttonStyle = {
    ...buttonBase,
    background: "#FFFFFF",
    color: "#D35400",
    boxShadow: hover
      ? "0 12px 30px rgba(211,84,0,0.18)"
      : "0 8px 20px rgba(0,0,0,0.12)",
    transform: hover ? "translateY(-4px)" : "translateY(0)",
  };

  return (
    <div className="tb-landing">
      <div className="tb-container">
        <div className="tb-logo-wrap">
          <img
            src="../../static/tiger.ico"
            alt="Tiger logo"
            className="tb-logo"
          />
        </div>

        <div className="tb-title">TigerBites</div>

        <p className="tb-lead">
          Discover the perfect place to eat at Princeton. Find restaurants, explore menus, read reviews, and connect with friends.
        </p>

        <p className="tb-sub">
          Update your preferences in your profile, create groups with friends, get personalized recommendations, and explore restaurants on our map. Find what satisfies your cravings instantly.
        </p>

        <div className="tb-cta-wrap">
          <a href="/discover" style={{ textDecoration: "none" }}>
            <button
              className="tb-cta"
              onMouseEnter={() => setHover(true)}
              onMouseLeave={() => setHover(false)}
              aria-label="Get started with TigerBites"
            >
              <span>Get Started</span>
              <span className="tb-cta-arrow">→</span>
            </button>
          </a>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
