import React from "react";
import RestaurantCard from "./RestaurantCard.jsx";

const RestaurantList = ({ restaurants }) => {
  if (!restaurants || restaurants.length === 0) {
    return <p>No restaurants found.</p>;
  }

  return (
    <section className="list">
      <h2>Restaurants</h2>
      {restaurants.map((rest) => (
        <RestaurantCard key={rest.id} rest={rest} />
      ))}
    </section>
  );
};

export default RestaurantList;
