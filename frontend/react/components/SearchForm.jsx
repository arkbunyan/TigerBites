import React, { useState } from "react";

const SearchForm = ({ onSearch }) => {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");

  const triggerSearch = (newName, newCategory) => {
    onSearch({ name: newName, category: newCategory });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    triggerSearch(name, category);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="container mt-4 mb-4 p-3 border rounded bg-light shadow-sm"
    >
      <div className="row align-items-end g-3">
        <div className="col-md-5">
          <label htmlFor="name" className="form-label fw-semibold">
            Restaurant Name
          </label>
          <input
            id="name"
            type="text"
            className="form-control"
            placeholder="Enter restaurant name"
            value={name}
            onChange={(e) => {
              const value = e.target.value;
              setName(value);
              triggerSearch(value, category);
            }}
          />
        </div>

        <div className="col-md-5">
          <label htmlFor="category" className="form-label fw-semibold">
            Category
          </label>
          <input
            id="category"
            type="text"
            className="form-control"
            placeholder="e.g. Mexican, Pizza, Ice Cream"
            value={category}
            onChange={(e) => {
              const value = e.target.value;
              setCategory(value);
              triggerSearch(name, value);
            }}
          />
        </div>

        <div className="col-md-2">
          <button
            type="submit"
            className="btn btn-dark w-100 fw-semibold"
            style={{ marginTop: "30px", backgroundColor: "#FF5F0D" }}
          >
            Search
          </button>
        </div>
      </div>
    </form>
  );
};

export default SearchForm;
