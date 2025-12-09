import React from "react";
import { Link } from "react-router-dom";

const RestaurantCard = ({ rest, compact = false }) => {
  return (
    <Link
      to={`/restaurants/${rest.id}`}
      className="text-decoration-none text-dark fw-bold"
    >
      <div
        className={`card shadow-sm mb-4 ${compact ? '' : 'h-100'}`}
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
              objectFit: "cover"
            }}
          />
        )}

        <div className="card-body">
          <h5 className="card-title">{rest.name}</h5>

          <p className="card-text mb-1 text-muted">{rest.category}</p>
          {!compact && (
            <>
              <p className="card-text mb-1">
                <small className="text-secondary">{rest.hours}</small>
              </p>
              <p className="card-text mb-2">
                <strong>Avg price:</strong> ${rest.avg_price}
              </p>
              {rest.website_url && (
                <a
                  href={rest.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-sm btn-outline-primary"
                  onClick={(e) => e.preventDefault()}
                >
                  Website
                </a>
              )}
            </>
          )}
        </div>
      </div>
    </Link>
  );
};

export default RestaurantCard;
