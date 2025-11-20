import React from "react";
import RestaurantCard from "./RestaurantCard.jsx";

const RestaurantList = ({ restaurants }) => {
  if (!restaurants || restaurants.length === 0) {
    return <p>No restaurants found.</p>;
  }

  return (
    <section className="container mt-4">
      <h2 className="mb-3">Restaurants</h2>
      <div className="row g-3">
        {restaurants.map((rest) => (
          <div key={rest.id} className="col-md-4 col-sm-6 mb-3 d-flex">
            <RestaurantCard rest={rest} />
          </div>
        ))}
      </div>
    </section>
  );
};

export default RestaurantList;
