import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import RestaurantPage from "./pages/RestaurantPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import MapPage from "./pages/MapPage.jsx";
import LogoutPage from "./pages/LogoutPage.jsx";
import LogoutCasPage from "./pages/LogoutCasPage.jsx";
import LogoutCasLandingPage from "./pages/LogoutCasLandingPage.jsx";
import GroupsPage from "./pages/GroupPage.jsx";
import HeaderNav from "./components/HeaderNav.jsx";

const App = () => {
  return (
    <Router>
      <div>
        <HeaderNav />

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/restaurants/:restId" element={<RestaurantPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/group" element={<GroupsPage />} />
          <Route path="/logout_app" element={<LogoutPage />} />
          <Route path="/logout_cas" element={<LogoutCasPage />} />
          <Route
            path="/logout_cas_landing"
            element={<LogoutCasLandingPage />}
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
