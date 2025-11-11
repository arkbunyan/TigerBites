import React, { useEffect, useState } from "react";
import RestaurantList from "../components/RestaurantList.jsx";
import SearchForm from "../components/SearchForm.jsx";

export default function HomePage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("/home")
      .then((res) => res.json())
      .then((data) => setData(data));
  }, []);

  if (!data) return <p>Loading...</p>;

  return (
    <div>
      <SearchForm />
      <RestaurantList restaurants={data.restaurants} />
    </div>
  );
}
