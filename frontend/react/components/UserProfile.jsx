import React from "react";

const UserProfile = ({ user }) => {
  if (!user) return <p>No user data provided.</p>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>
        {user.email} {user.phone ? `· ${user.phone}` : ""}
      </p>

      <h3>Favorite Restaurants</h3>
      {user.favoriteRestaurants && user.favoriteRestaurants.length > 0 ? (
        <ul>
          {user.favoriteRestaurants.map((item) => (
            <li key={item.id || item.name}>
              <strong>{item.name}</strong>
              {item.price && ` — ${item.price}`}
              {item.description && (
                <>
                  <br />
                  {item.description}
                </>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p>No menu yet.</p>
      )}
    </div>
  );
};

export default UserProfile;
