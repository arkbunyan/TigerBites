import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import DiscoverPage from "./pages/DiscoverPage.jsx";
import RestaurantPage from "./pages/RestaurantPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import MapPage from "./pages/MapPage.jsx";
import LogoutPage from "./pages/LogoutPage.jsx";
import LogoutCasPage from "./pages/LogoutCasPage.jsx";
import LogoutCasLandingPage from "./pages/LogoutCasLandingPage.jsx";
import GroupsPage from "./pages/GroupPage.jsx";
import HeaderNav from "./components/HeaderNav.jsx";
import HomePage from "./pages/HomePage.jsx";
import BackOffice_Home from "./pages/backoffice/BackOffice_Home.jsx";
import BackOffice_Restaurant from "./pages/backoffice/BackOffice_Restaurant.jsx"
import BackOffice_Feedback from "./pages/backoffice/BackOffice_Feedback.jsx";
import BackOffice_Reviews from "./pages/backoffice/BackOffice_Reviews.jsx";

const App = () => {
  return (
    <Router>
      <div>
        <HeaderNav />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/discover" element={<DiscoverPage />} />
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
          <Route path="/back_office" element={<BackOffice_Home />} />
          <Route path="/back_office/restaurants/:restId" element={<BackOffice_Restaurant />} />
          <Route path="/back_office/feedback" element={<BackOffice_Feedback />} />
          <Route path="/back_office/reviews" element={<BackOffice_Reviews />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
