import React from "react";

const HomePage = () => {
  return (
    <div>
      <div className="d-flex align-items-center">
        <img
          src="../static/nassaustreet.png"
          alt="Tiger logo"
          style={{ height: "44px", width: "44px", marginRight: "10px" }}
        />
      </div>
      <div className="card vh-100 vw-100 d-flex justify-content-center align-items-center position-relative">
        <img
          className="card-img"
          src="../static/nassaustreet.jpeg"
          alt="Card image"
        ></img>
        <div className="card-img-overlay bg-dark bg-opacity-50">
          <h1 className="text-white fw-bold position-relative">
            Welcome to TigerBites
          </h1>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
