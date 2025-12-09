import React from "react";
import { Link } from "react-router-dom";

const FeedbackCard = ({ response }) => {
  return (
    <div
      className="text-decoration-none text-dark fw-bold"
    >
      <div
        className="card shadow-sm mb-4 h-100"
        style={{ borderRadius: "12px" }}
      >
        {rest.picture && (
          <img
            src={rest.picture}
            alt={rest.name}
            className="card-img-top"
            style={{
              borderTopLeftRadius: "12px",
              borderTopRightRadius: "12px",
            }}
          />
        )}

        <div className="card-body">
          <h5 className="card-title">{response.name}</h5>

          <p className="card-text mb-1 text-muted">{rest.category}</p>
          
        </div>
      </div>
    </div>
  );
};

export default FeedbackCard;
