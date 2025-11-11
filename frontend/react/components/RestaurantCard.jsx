import React from "react";

const RestaurantCard = ({ rest }) => {
  return (
    <div className="result">
      <h3>
        <a href={`/restaurant/${rest.id}`}>{rest.name}</a>
      </h3>

      <p>{rest.category}</p>
      <p>{rest.hours}</p>
      <p>Avg price: {rest.avg_price}</p>

      <hr />
    </div>
  );
};

export default RestaurantCard;
