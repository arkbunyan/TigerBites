import React from "react";
import { Link } from "react-router-dom";

const RestaurantCard = ({ rest }) => {
  return (
    <div className="card shadow-sm mb-4" style={{ borderRadius: "12px" }}>
      <div className="card-body">
        <h5 className="card-title">
          <Link
            to={`/restaurants/${rest.id}`}
            className="text-decoration-none text-dark fw-bold"
          >
            {rest.name}
          </Link>
        </h5>

        <p className="card-text mb-1 text-muted">{rest.category}</p>
        <p className="card-text mb-1">
          <small className="text-secondary">{rest.hours}</small>
        </p>
        <p className="card-text">
          <strong>Avg price:</strong> ${rest.avg_price}
        </p>
      </div>
    </div>
  );
};

export default RestaurantCard;
