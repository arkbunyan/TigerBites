import React, { useState } from "react";
import Header from "./components/Header.jsx";
import Navbar from "./components/Navbar.jsx";
import SearchForm from "./components/SearchForm.jsx";
import RestaurantList from "./components/RestaurantList.jsx";
import HomePage from "./pages/HomePage.jsx";

const App = () => {
  const [restaurants, setRestaurants] = useState([]);

  const handleSearch = (query) => {
    // Replace this with your API call
    console.log("Search query:", query);

    // Example: fetch restaurants from backend
    // fetch(`/api/search?name=${query.name}&category=${query.category}`)
    //   .then(res => res.json())
    //   .then(data => setRestaurants(data.restaurants));

    // For now, just a dummy example
    setRestaurants([
      { id: 1, name: "Pizza Place", category: "Italian", avg_price: "$$" },
      { id: 2, name: "Sushi Spot", category: "Japanese", avg_price: "$$$" },
    ]);
  };

  return (
    <div className="container">
      <Header />
      <Navbar />
      <HomePage />
    </div>
  );
};

export default App;
