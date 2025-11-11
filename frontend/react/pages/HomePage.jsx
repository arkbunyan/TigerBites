import React, { useEffect, useState } from "react";
import RestaurantList from "../components/RestaurantList.jsx";
import SearchForm from "../components/SearchForm.jsx";

export default function HomePage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("/api/home")
      .then((res) => res.json())
      .then((data) => setData(data));
  }, []);

  // Function to call search API
  const handleSearch = ({ name, category }) => {
    const params = new URLSearchParams();
    if (name) params.append("name", name);
    if (category) params.append("category", category);

    fetch(`/api/search?${params.toString()}`)
      .then((res) => res.json())
      .then((result) => {
        if (result.error) {
          console.error(result.error);
          setData({ restaurants: [] });
        } else {
          setData({ restaurants: result.restaurants });
        }
      })
      .catch((err) => {
        console.error(err);
        setData({ restaurants: [] });
      });
  };

  if (!data) return <p>Loading...</p>;

  return (
    <div>
      <SearchForm onSearch={handleSearch} />
      <RestaurantList restaurants={data.restaurants} />
    </div>
  );
}
