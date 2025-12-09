import React, { useEffect, useState } from "react";

const steps = [
  {
    title: "Discover",
    body:
      "Browse and search restaurants. Click a card to see details, menu items, and reviews.",
    actionLabel: "Go to Discover",
    href: "/discover",
  },
  {
    title: "Profile",
    body:
      "Set your favorite cuisines, allergies, and dietary restrictions to get personalized recommendations with groups.",
    actionLabel: "Open Profile",
    href: "/profile",
  },
  {
    title: "Groups",
    body:
      "Create a group with friends and see recommended restaurants based on shared preferences.",
    actionLabel: "View Groups",
    href: "/group",
  },
  {
    title: "Map",
    body:
      "Explore restaurant locations around campus and quickly navigate to your chosen spot.",
    actionLabel: "Open Map",
    href: "/map",
  },
];

const TutorialModal = ({ open, onClose }) => {
  const [idx, setIdx] = useState(0);
  const step = steps[idx];

  useEffect(() => {
    if (open) {
      // lock scroll when modal open
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = "auto";
      };
    }
  }, [open]);

  if (!open) return null;

  const next = () => setIdx((i) => Math.min(i + 1, steps.length - 1));
  const prev = () => setIdx((i) => Math.max(i - 1, 0));

  const closeAndRemember = () => {
    try {
      localStorage.setItem("tb_seen_tutorial", "1");
    } catch {}
    onClose?.();
  };

  return (
    <div
      className="position-fixed top-0 start-0 w-100 h-100"
      style={{ zIndex: 1050 }}
    >
      {/* Backdrop */}
      <div
        className="w-100 h-100"
        style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
        onClick={closeAndRemember}
      />
      {/* Modal card */}
      <div
        className="position-absolute top-50 start-50 translate-middle card shadow"
        style={{ maxWidth: 560, width: "92%", borderRadius: 12 }}
      >
        <div className="card-header d-flex justify-content-between align-items-center">
          <span className="fw-bold">Welcome to TigerBites</span>
          <button className="btn btn-sm btn-outline-secondary" onClick={closeAndRemember}>
            Skip
          </button>
        </div>
        <div className="card-body">
          <div className="mb-2 text-uppercase small text-muted">Step {idx + 1} of {steps.length}</div>
          <h5 className="card-title mb-2">{step.title}</h5>
          <p className="card-text">{step.body}</p>
          <div className="d-flex gap-2 mt-3">
            <button
              className="btn btn-outline-secondary"
              onClick={prev}
              disabled={idx === 0}
            >
              Back
            </button>
            {idx < steps.length - 1 ? (
              <button className="btn" style={{ backgroundColor: "#FF5F0D", color: "white" }} onClick={next}>
                Next
              </button>
            ) : (
              <button className="btn" style={{ backgroundColor: "#FF5F0D", color: "white" }} onClick={closeAndRemember}>
                Finish
              </button>
            )}
            <a className="btn btn-light ms-auto" href={step.href} onClick={closeAndRemember}>
              {step.actionLabel}
            </a>
          </div>
        </div>
        <div className="card-footer bg-white">
          <div className="form-check">
            <input
              className="form-check-input"
              type="checkbox"
              id="dontShowAgain"
              onChange={(e) => {
                try {
                  localStorage.setItem("tb_seen_tutorial", e.target.checked ? "1" : "0");
                } catch {}
              }}
            />
            <label className="form-check-label" htmlFor="dontShowAgain">
              Don't show again
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TutorialModal;