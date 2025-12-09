import React from "react";

const HomePage = () => {
  return (
    <div>
      <div className="card vh-100 vw-100 d-flex justify-content-center align-items-center position-relative">
        <img
          src="../../static/tiger.ico"
          alt="Tiger logo"
          style={{
            height: "100%",
            width: "100%",
            objectFit: "contain",
            backgroundColor: "#FF5F0D",
          }}
        />
        <div className="card-img-overlay bg-dark bg-opacity-50">
          <h1 className="text-white text-center fw-bold position-relative">
            Welcome to TigerBites
          </h1>
          <p className="text-white text-center mt-4 position-relative h5">
            “Where do you want to eat?” — A question that everyone has been
            asked before. TigerBites provides the
            quickest and easiest way for members of the Princeton community to
            find the perfect restaurant to satisfy their cravings–fast. Equipped
            with menu listings, reviews, and detailed location information,
            you can find the best restaurant for your current craving.
            TigerBites is sure to find what’s right for you.
          </p>

          <p className="text-white text-center mt-4 position-relative h3">
            Start by navigating to your profile and updating your preferences
            and dietary restrictions. Then, the next time you and a group of
            friends are deciding where to eat, create a group and check out the
            recommended options! To see where your chosen restaurant is, head
            over to the map page. Happy eating!
          </p>
          <a
            href="/discover"
            className="link-underline-light d-flex justify-content-center mt-4 position-relative"
          >
            <button type="button" class="btn btn-light">
              Click here to Login!
            </button>
          </a>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
