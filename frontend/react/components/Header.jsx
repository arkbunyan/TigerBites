import React, { useState, useEffect } from "react";

const Header = () => {
  const [user, setUser] = useState(null);
  const [datetime, setDatetime] = useState(new Date());

  // Fetch user info on component mount
  useEffect(() => {
    fetch("/api/profile")
      .then((res) => {
        if (res.ok) return res.json();
        return null;
      })
      .then((data) => setUser(data))
      .catch(() => setUser(null));
  }, []);


  let greeting = "Welcome to Tiger Bites!";

  return (
    <div className="header-container">
      <h1>{greeting}</h1>
      <div className="header-info">
        {user && (
          <div className="user-info">
            <span>Signed in as {user.firstname || user.username || ''}</span>
          </div>
        )}
      </div>
      <hr />
    </div>
  );
};

export default Header;
