import React from "react";
import { Link } from "react-router-dom";

const LogoutPage = () => {
  return (
    <div className="logout-page">
      <h2>You are logged out of Tiger Bites</h2>
      <p>
        Click to <Link to="/">Revisit TigerBites</Link>
      </p>
      <hr />
      <p>
        Created by the Tiger Bites Team
      </p>
    </div>
  );
};

export default LogoutPage;
