import React, { useState } from "react";

const RestaurantDetails = ({ restaurant, menuItems, reviews = [] }) => {
  const [isOpen, setIsOpen] = useState(false);

  const averageRating =
    reviews.length > 0
      ? (
          reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
        ).toFixed(1)
      : null;

  if (!restaurant)
    return <p className="text-center mt-4">No restaurant data provided.</p>;

  return (
    <div className="container my-5">
      <div className="card shadow-sm border-0 mb-4">
        {restaurant.picture && (
          <img
            src={restaurant.picture}
            className="card-img-top"
            style={{
              height: "350px",
              width: "100%",
              borderTopLeftRadius: "12px",
              borderTopRightRadius: "12px",
              objectFit: "cover",
            }}
          />
        )}
        <div className="card-body">
          <h2
            className="card-title fw-bold"
            style={{
              color: "#FF5F0D",
            }}
          >
            {restaurant.name}
          </h2>
          <p className="card-text text-muted mb-1">
            {restaurant.category}{" "}
            {restaurant.hours && (
              <span className="text-secondary">· {restaurant.hours}</span>
            )}
          </p>
          {restaurant.location && (
            <p className="text-secondary mb-0">📍 {restaurant.location}</p>
          )}
          {restaurant.avg_price && (
            <p className="text-secondary mb-0">
              💰 Average price: ${restaurant.avg_price}
            </p>
          )}
          {restaurant.yelp_rating && (
            <p className="text-secondary mb-0">
              ❗Yelp rating: {restaurant.yelp_rating} / 5
            </p>
          )}
          {averageRating && (
            <p className="text-secondary mb-0">
              ⭐ TigerBites user rating: {averageRating} / 5 ({reviews.length}{" "}
              reviews)
            </p>
          )}

          {restaurant.website_url && (
            <p className="mt-3">
              <a
                href={restaurant.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary btn-sm"
              >
                Visit Website
              </a>
            </p>
          )}
        </div>
      </div>

      <div
        className="card shadow-sm border-0"
        style={{ backgroundColor: "#e6e6e6" }}
      >
        <div className="card-body">
          <div
            onClick={() => setIsOpen(!isOpen)}
            className="d-flex justify-content-between align-items-center mb-3"
            style={{ cursor: "pointer" }}
          >
            <h3 className="card-title mb-0 text-dark">Menu</h3>
            <span
              style={{
                fontSize: "1.2rem",
                transition: "transform 0.2s ease",
                transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
              }}
            >
              ▼
            </span>
          </div>

          {isOpen && (
            <>
              {menuItems && menuItems.length > 0 ? (
                <div className="list-group">
                  {menuItems.map((item) => (
                    <div
                      key={item.id || item.name}
                      className="list-group-item border-0 border-bottom py-3"
                    >
                      <div className="d-flex justify-content-between align-items-center">
                        <strong className="fs-5">{item.name}</strong>
                        {item.price && (
                          <span className="text-muted">${item.price}</span>
                        )}
                      </div>
                      {item.description && (
                        <p className="text-secondary mb-0 mt-1">
                          {item.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted fst-italic">No menu yet.</p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default RestaurantDetails;
