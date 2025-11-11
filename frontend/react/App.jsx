import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header.jsx";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";
import RestaurantPage from "./pages/RestaurantPage.jsx";

const App = () => {
  return (
    <Router>
      <div className="container">
        <Header />
        <Navbar />

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/restaurants/:restId" element={<RestaurantPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
