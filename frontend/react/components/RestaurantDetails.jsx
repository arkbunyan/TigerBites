import React from "react";

const RestaurantDetails = ({ restaurant, menuItems }) => {
  if (!restaurant) return <p>No restaurant data provided.</p>;

  return (
    <div>
      <h2>{restaurant.name}</h2>
      <p>
        {restaurant.category} {restaurant.hours ? `· ${restaurant.hours}` : ""}
      </p>

      <h3>Menu</h3>
      {menuItems && menuItems.length > 0 ? (
        <ul>
          {menuItems.map((item) => (
            <li key={item.id || item.name}>
              <strong>{item.name}</strong>
              {item.price && ` — ${item.price}`}
              {item.description && (
                <>
                  <br />
                  {item.description}
                </>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p>No menu yet.</p>
      )}
    </div>
  );
};

export default RestaurantDetails;
