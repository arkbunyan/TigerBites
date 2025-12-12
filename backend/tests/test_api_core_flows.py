from backend import database


def _login_session(client, username="apitest_user"):
    with client.session_transaction() as sess:
        sess["user_info"] = {
            "user": username,
            "attributes": {
                "givenname": ["Api"],
                "displayname": ["Api Test"],
                "mail": ["apitest@example.com"],
            },
        }


def _get_any_restaurant_id():
    ok, restaurants = database.load_all_restaurants()
    assert ok and restaurants
    return restaurants[0]["id"]


def _create_review(client, username, rest_id, rating=5, comment="Automated test review"):
    _login_session(client, username=username)
    resp = client.post(
        f"/api/restaurants/{rest_id}/reviews",
        json={"rating": rating, "comment": comment},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert "review" in body
    return body["review"]


def test_home_endpoint_returns_restaurants_and_prefs(client):
    username = "home_tester"
    _login_session(client, username=username)

    resp = client.get("/api/home")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "restaurants" in data
    assert isinstance(data["restaurants"], list)
    assert len(data["restaurants"]) >= 1
    assert data["firstname"] != ""
    assert "preferences" in data
    assert isinstance(data["preferences"], dict)


def test_map_endpoint_returns_restaurants(client):
    username = "map_tester"
    _login_session(client, username=username)

    resp = client.get("/api/map")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "restaurants" in data
    assert isinstance(data["restaurants"], list)


def test_search_endpoint_basic(client):
    ok_all, restaurants = database.load_all_restaurants()
    assert ok_all and restaurants
    sample = restaurants[0]
    name = sample["name"]
    query = name[:3]

    resp = client.get("/api/search", query_string={"name": query, "category": ""})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "restaurants" in data
    ids = [r["id"] for r in data["restaurants"]]
    assert sample["id"] in ids


def test_search_endpoint_empty_filters_matches_all(client):
    ok_all, all_rows = database.load_all_restaurants()
    assert ok_all

    resp = client.get("/api/search")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "restaurants" in data
    assert len(data["restaurants"]) == len(all_rows)


def test_restaurant_details_and_menu(client):
    rest_id = _get_any_restaurant_id()
    resp = client.get(f"/api/restaurants/{rest_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["restaurant"]["id"] == rest_id
    assert "menu" in data
    assert isinstance(data["menu"], list)


def test_profile_get_and_update(client):
    username = "profile_tester"

    ok_upsert, _ = database.upsert_user(
        username,
        "profile_tester@example.com",
        "Profile",
        "Profile Tester",
    )
    assert ok_upsert

    _login_session(client, username=username)

    resp = client.get("/api/profile")
    assert resp.status_code == 200
    profile = resp.get_json()
    assert profile["username"] == username

    new_data = {
        "favorite_cuisine": ["Mexican", "Italian"],
        "allergies": ["Peanuts"],
        "dietary_restrictions": ["Vegetarian"],
    }
    resp = client.put("/api/profile", json=new_data)
    assert resp.status_code == 200
    updated = resp.get_json()
    assert updated["favorite_cuisine"] == new_data["favorite_cuisine"]
    assert isinstance(updated["allergies"], list)
    assert isinstance(updated["dietary_restrictions"], list)


def test_cuisines_endpoint(client):
    username = "cuisine_tester"
    _login_session(client, username=username)

    resp = client.get("/api/cuisines")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "cuisines" in data
    assert isinstance(data["cuisines"], list)
    assert len(data["cuisines"]) >= 1


def test_create_group_and_list_via_api(client):
    username = "group_owner"
    _login_session(client, username=username)

    resp = client.get("/api/groups")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "groups" in data

    resp = client.post("/api/groups", json={"group_name": "My Test Group"})
    assert resp.status_code == 201
    body = resp.get_json()
    group = body["group"]
    group_id = group["id"]

    resp = client.get("/api/groups")
    assert resp.status_code == 200
    data = resp.get_json()
    ids = [g["id"] for g in data["groups"]]
    assert group_id in ids


def test_create_review_and_fetch_back(client):
    username = "review_tester"
    rest_id = _get_any_restaurant_id()
    review = _create_review(
        client,
        username=username,
        rest_id=rest_id,
        comment="Automated test review",
    )

    resp = client.get(f"/api/restaurants/{rest_id}/reviews")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reviews" in data
    assert any(r.get("id") == review["id"] for r in data["reviews"])


def test_create_review_invalid_rating_and_long_comment(client):
    username = "review_invalid_tester"
    rest_id = _get_any_restaurant_id()
    _login_session(client, username=username)

    resp = client.post(
        f"/api/restaurants/{rest_id}/reviews",
        json={"rating": 10, "comment": "Too high rating"},
    )
    assert resp.status_code == 400
    err = resp.get_json()
    assert "Rating must be an integer between 1 and 5" in err.get("error", "")

    long_comment = "x" * 501
    resp = client.post(
        f"/api/restaurants/{rest_id}/reviews",
        json={"rating": 5, "comment": long_comment},
    )
    assert resp.status_code == 400
    err = resp.get_json()
    assert "Comment must be at most" in err.get("error", "")


def test_get_all_reviews_includes_test_review(client):
    username = "all_reviews_tester"
    rest_id = _get_any_restaurant_id()
    marker_comment = "Review visible in /api/reviews"
    review = _create_review(
        client,
        username=username,
        rest_id=rest_id,
        comment=marker_comment,
    )

    resp = client.get("/api/reviews")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reviews" in data
    ids = [r["id"] for r in data["reviews"]]
    assert review["id"] in ids


def test_user_reviews_and_delete_review(client):
    username = "delete_review_user"
    rest_id = _get_any_restaurant_id()
    marker_comment = "Review to delete"
    review = _create_review(
        client,
        username=username,
        rest_id=rest_id,
        comment=marker_comment,
    )

    _login_session(client, username=username)
    resp = client.get("/api/users/reviews")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reviews" in data
    ids = [r["id"] for r in data["reviews"]]
    assert review["id"] in ids

    resp = client.delete(f"/api/reviews/{review['id']}")
    assert resp.status_code == 200
    msg = resp.get_json()
    assert msg.get("message") == "Review deleted"

    _login_session(client, username=username)
    resp = client.get("/api/users/reviews")
    assert resp.status_code == 200
    data = resp.get_json()
    ids_after = [r["id"] for r in data["reviews"]]
    assert review["id"] not in ids_after


def test_submit_feedback_validation_and_success(client):
    username = "feedback_tester"
    rest_id = _get_any_restaurant_id()
    _login_session(client, username=username)

    url = f"/api/restaurants/{rest_id}/feedback"

    resp = client.post(url)
    assert resp.status_code in (400, 415)
    if resp.status_code == 400:
        err = resp.get_json()
        assert "No data provided" in err.get("error", "")

    resp = client.post(url, json={"response": "   "})
    assert resp.status_code == 400
    err = resp.get_json()
    assert "non-empty string" in err.get("error", "")

    resp = client.post(url, json={"response": "Nice atmosphere"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "feedback" in data
    feedback = data["feedback"]
    assert feedback["response"] == "Nice atmosphere"


def test_feedback_list_and_delete(client):
    username = "feedback_delete_user"
    rest_id = _get_any_restaurant_id()
    marker_response = "Feedback to delete"
    _login_session(client, username=username)

    resp = client.post(
        f"/api/restaurants/{rest_id}/feedback",
        json={"response": marker_response},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    feedback = data["feedback"]
    feedback_id = feedback["id"]

    resp = client.get(f"/api/restaurants/{rest_id}/feedback")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reviews" in data
    assert any(f.get("id") == feedback_id for f in data["reviews"])

    _login_session(client, username=username)
    resp = client.get("/api/feedback")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "responses" in data
    assert any(f.get("id") == feedback_id for f in data["responses"])

    _login_session(client, username=username)
    resp = client.delete(f"/api/feedback/{feedback_id}")
    assert resp.status_code in (200, 400, 403)
    body = resp.get_json()
    if resp.status_code == 200:
        assert body.get("message") == "Feedback deleted"
    else:
        assert "error" in body


def test_getusername_requires_auth(client):
    resp = client.get("/api/getusername")
    assert resp.status_code == 403


def test_getusername_with_session(client):
    username = "getusername_tester"
    _login_session(client, username=username)

    resp = client.get("/api/getusername")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("username") == username
