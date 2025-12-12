from backend import database


def test_load_all_restaurants_nonempty():
    ok, restaurants = database.load_all_restaurants()
    assert ok
    assert isinstance(restaurants, list)
    assert len(restaurants) >= 1

    sample = restaurants[0]
    for key in ["id", "name", "location", "category"]:
        assert key in sample


def test_restaurant_search_matches_name_substring():
    ok_all, restaurants = database.load_all_restaurants()
    assert ok_all and restaurants
    sample = restaurants[0]
    name = sample["name"]
    query = name[:3]

    ok, results = database.restaurant_search([query, ""])
    assert ok
    assert any(r["id"] == sample["id"] for r in results)


def test_restaurant_search_empty_filters_returns_everything():
    ok_all, all_rows = database.load_all_restaurants()
    assert ok_all

    ok, results = database.restaurant_search(["", ""])
    assert ok
    assert len(results) == len(all_rows)


def test_load_menu_for_some_restaurant():
    ok_all, restaurants = database.load_all_restaurants()
    assert ok_all and restaurants

    rest_id = restaurants[0]["id"]
    ok, items = database.load_menu_for_restaurant(rest_id)
    assert ok
    assert isinstance(items, list)


def test_available_cuisines_nonempty_and_strings():
    ok, cuisines = database.get_available_cuisines()
    assert ok
    assert isinstance(cuisines, list)
    assert len(cuisines) >= 1
    assert all(isinstance(c, str) for c in cuisines)


def test_create_group_and_list_for_user():
    username = "test_group_user"

    ok_user, _ = database.upsert_user(
        username, "test@example.com", "Test", "Test User"
    )
    assert ok_user

    ok_group, group = database.create_group("Testing Group", username)
    assert ok_group
    group_id = group["id"]

    ok_list, groups = database.list_groups_for_user(username)
    assert ok_list
    ids = [g["id"] for g in groups]
    assert group_id in ids

    ok_prefs, prefs = database.get_group_preferences(group_id)
    assert ok_prefs
    assert isinstance(prefs, dict)
    for key in ["recommended_cuisines", "dietary_restrictions", "allergies"]:
        assert key in prefs


def test_get_user_by_username_round_trip():
    username = "db_user_test"
    email = "db_user@example.com"
    firstname = "DB"
    fullname = "DB User"

    ok_upsert, _ = database.upsert_user(username, email, firstname, fullname)
    assert ok_upsert

    ok_get, user_data = database.get_user_by_username(username)
    assert ok_get
    assert user_data["netid"] == username
    assert user_data["email"] == email
    assert user_data["firstname"] == firstname
    assert user_data["fullname"] == fullname
