import { expectedError } from "@babel/core/lib/errors/rewrite-stack-trace";
import React, { useState, useEffect } from "react";

const RestaurantDetails = ({ restaurant, menuItems }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [editedRestaurant, setEditedRestaurant] = useState({
    name: "",
    category: "",
    hours: "",
    location: "",
    avg_price: "",
    yelp_rating: "",
    picture: ""
});
  const [editedMenu, setEditedMenu] = useState(menuItems || []);
  const [isSaving, setIsSaving] = useState(false);
  
  useEffect(() => {
  if (restaurant) setEditedRestaurant(restaurant);
  if (menuItems) setEditedMenu(menuItems);
}, [restaurant, menuItems]);


  if (!restaurant)
    return <p className="text-center mt-4">No restaurant data provided.</p>;

  const handleRestaurantChange = (field, value) => {
    setEditedRestaurant((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleMenuChange = (index, field, value) => {
    const updatedMenu = [...editedMenu];
    updatedMenu[index][field] = value;
    setEditedMenu(updatedMenu);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving


    try {
      const response = await fetch(`/api/restaurants/${restaurant.id}/update`, {
        method: "PUT",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ editedRestaurant }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      const data = await response.json();
    } catch (err) {
      console.error("Failed to update restaurant:", err);
    } finally {
      setIsSaving(false)
    }
    };

  
  return (
    <div className="container my-5">
      <h2>  
        Edit {editedRestaurant.name}
      </h2>
        <div className="card shadow-sm border-0 mb-4">
          {editedRestaurant.picture && (
            <img
              src={editedRestaurant.picture}
              className="card-img-top"
              style={{
                height: "350px",
                width: "100%",
                borderTopLeftRadius: "12px",
                borderTopRightRadius: "12px",
                objectFit: "cover",
              }}
            />
          )}

          <button
            className="btn btn-primary mt-2"
            onClick={handleSubmit}
            disabled={isSaving}
          >
            {isSaving ? "Saving..." : "Save Changes"}
          </button>


          <div className="card-body">
            {/*NAME */}
            Name:
            <input
              className="form-control mb-2"
              value={editedRestaurant.name || ""}
              onChange={(e) =>
                handleRestaurantChange("name", e.target.value)
              }
            />

            {/*CATEGORY*/}
            Category:
            <input
              className="form-control mb-2"
              value={editedRestaurant.category || ""}
              onChange={(e) =>
                handleRestaurantChange("category", e.target.value)
              }
            />

            {/*HOURS*/}
            Hours:
            <input
              className="form-control mb-2"
              value={editedRestaurant.hours || ""}
              onChange={(e) =>
                handleRestaurantChange("hours", e.target.value)
              }
            />

            {/*LOCATION*/}
            Location:
            <input
              className="form-control mb-2"
              value={editedRestaurant.location || ""}
              onChange={(e) =>
                handleRestaurantChange("location", e.target.value)
              }
            />

            {/*PRICE*/}
            Avg Price:
            <input
              type="number"
              className="form-control mb-2"
              value={editedRestaurant.avg_price || ""}
              onChange={(e) =>
                handleRestaurantChange("avg_price", e.target.value)
              }
            />

            {/*YELP*/}
            Yelp Rating
            <input
              type="number"
              step="0.1"
              className="form-control"
              value={editedRestaurant.yelp_rating || ""}
              onChange={(e) =>
                handleRestaurantChange("yelp_rating", e.target.value)
              }
            />
          </div>
        </div>

        {/* MENU */}
        <div className="card shadow-sm border-0">
          <div className="card-body">
            <div
              onClick={() => setIsOpen(!isOpen)}
              className="d-flex justify-content-between align-items-center mb-3"
              style={{ cursor: "pointer" }}
            >
              <h3 className="card-title mb-0 text-dark">Menu</h3>
              <span
                style={{
                  fontSize: "1.2rem",
                  transition: "transform 0.2s ease",
                  transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
                }}
              >
                ▼
              </span>
            </div>

            {isOpen && (
              <>
                {editedMenu.length > 0 ? (
                  <div className="list-group">
                    {editedMenu.map((item, index) => (
                      <div
                        key={item.id || index}
                        className="list-group-item border-0 border-bottom py-3"
                      >
                        <input
                          className="form-control mb-1"
                          value={item.name}
                          onChange={(e) =>
                            handleMenuChange(index, "name", e.target.value)
                          }
                        />

                        <input
                          type="number"
                          className="form-control mb-1"
                          value={item.price || ""}
                          onChange={(e) =>
                            handleMenuChange(index, "price", e.target.value)
                          }
                        />

                        <textarea
                          className="form-control"
                          value={item.description || ""}
                          onChange={(e) =>
                            handleMenuChange(index, "description", e.target.value)
                          }
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted fst-italic">No menu yet.</p>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    );
};

export default RestaurantDetails;
