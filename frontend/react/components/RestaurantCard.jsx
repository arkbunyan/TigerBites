import React from "react";
import { Link } from "react-router-dom";

const RestaurantCard = ({ rest }) => {
  return (
    <div className="result">
      <h3>
        <Link to={`/restaurants/${rest.id}`}>{rest.name}</Link>
      </h3>

      <p>{rest.category}</p>
      <p>{rest.hours}</p>
      <p>Avg price: {rest.avg_price}</p>

      <hr />
    </div>
  );
};

export default RestaurantCard;
