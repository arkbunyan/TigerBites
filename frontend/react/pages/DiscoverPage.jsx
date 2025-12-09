import React, { useEffect, useState } from "react";
import RestaurantList from "../components/RestaurantList.jsx";
import SearchForm from "../components/SearchForm.jsx";

const DiscoverPage = () => {
  const [data, setData] = useState(null);
  const [preferredCuisines, setPreferredCuisines] = useState([]);

  useEffect(() => {
    fetch("/api/home")
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        // Try to pull user preferences if available on the home payload or via a dedicated endpoint
        // If home does not include preferences, we can fetch from /api/profile or a preferences route
        // Here, we infer from data if present; otherwise leave empty
        const prefs = (data.preferences && data.preferences.favorite_cuisines) || [];
        setPreferredCuisines((prefs || []).map((c) => String(c).trim().toLowerCase()));
      });
  }, []);

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

  // Sort restaurants so preferred cuisines appear first, preserving relative order otherwise
  const restaurants = Array.isArray(data.restaurants) ? [...data.restaurants] : [];
  const preferredSet = new Set(preferredCuisines);
  const sorted = restaurants.sort((a, b) => {
    const ca = String(a.category || '').trim().toLowerCase();
    const cb = String(b.category || '').trim().toLowerCase();
    const aPref = preferredSet.has(ca) ? 1 : 0;
    const bPref = preferredSet.has(cb) ? 1 : 0;
    // Prefer those matching user's cuisines
    if (aPref !== bPref) return bPref - aPref;
    return 0;
  });

  return (
    <div>
      <SearchForm onSearch={handleSearch} />
  <RestaurantList restaurants={sorted} />
    </div>
  );
};

export default DiscoverPage;
