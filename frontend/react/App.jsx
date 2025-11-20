import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header.jsx";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";
import RestaurantPage from "./pages/RestaurantPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import MapPage from "./pages/MapPage.jsx";
import { APIProvider } from "@vis.gl/react-google-maps";
import GroupsPage from "./pages/GroupPage.jsx";

const App = () => {
  return (
    <Router>
      <div className="container">
        <Header />
        <Navbar />

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/restaurants/:restId" element={<RestaurantPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/group" element={<GroupsPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
