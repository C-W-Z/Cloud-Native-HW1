import pytest
import random
from cloudshop.service import ServiceAPI
from cloudshop.dao import Database

@pytest.fixture
def mock_db():
    db = Database(":memory:")
    return db


@pytest.fixture
def api(mock_db):
    return ServiceAPI(mock_db)


def test_register_user(api):
    assert api.register("user1") == "Success"
    assert api.register("user1") == "Error - user already existing"


def test_create_listing(api):
    api.register("user1")
    listing_id = api.create_listing(
        "user1", "Phone model 8", "Black color, brand new", 1000, "Electronics"
    )
    assert str(listing_id).isdigit()
    assert str(listing_id) == "100001"

    assert (
        api.create_listing("unknown_user", "T-shirt", "White color", 20, "Sports")
        == "Error - unknown user"
    )


def test_get_listing(api):
    api.register("user1")
    listing_id = api.create_listing(
        "user1", "Phone model 8", "Black color, brand new", 24.86, "Electronics"
    )
    response = api.get_listing("user1", listing_id)
    assert "Phone model 8|Black color, brand new|24.86|" in response
    assert "|Electronics|user1" in response

    assert api.get_listing("user1", "999999") == "Error - not found"
    assert api.get_listing("X", listing_id) == "Error - unknown user"


def test_delete_listing(api):
    api.register("user1")
    api.register("user2")

    listing_id = api.create_listing(
        "user1", "Black shoes", "Training shoes", 100, "Sports"
    )

    assert api.delete_listing("user2", listing_id) == "Error - listing owner mismatch"
    assert api.delete_listing("user1", listing_id) == "Success"
    assert api.delete_listing("user1", listing_id) == "Error - listing does not exist"


def test_get_category(api):
    api.register("user1")
    api.register("user2")

    api.create_listing("user1", "Shoes", "Running shoes", 50, "Sports")
    api.create_listing("user2", "Jersey", "Football jersey", 30, "Sports")

    response = api.get_category("user1", "Sports")
    assert "Shoes|Running shoes|50" in response
    assert "Jersey|Football jersey|30" in response

    assert api.get_category("user1", "X") == "Error - category not found"
    assert api.get_category("X", "Sports") == "Error - unknown user"


def test_get_top_category(api):
    api.register("user1")
    api.register("user2")

    api.create_listing("user1", "Shoes", "Running shoes", 50, "Sports")
    api.create_listing("user1", "Football", "Game ball", 20, "Sports")
    api.create_listing("user2", "Jersey", "Football jersey", 30, "Fashion")

    assert api.get_top_categories("user1") == "Sports"
    assert api.get_top_categories("X") == "Error - unknown user"


def test_get_top_category_multiple(api):
    NUM_USERS = 20
    NUM_CATEGORIES = 15
    NUM_LISTINGS = 100

    # Create object
    users = [f"user{i}" for i in range(1, NUM_USERS + 1)]
    categories = [f"Category{i}" for i in range(1, NUM_CATEGORIES + 1)]

    for user in users:
        api.register(user)

    listings_per_user = {user: [] for user in users}
    listings_per_category = {category: 0 for category in categories}

    for _ in range(NUM_LISTINGS):
        user = random.choice(users)
        category = random.choice(categories)
        listing_id = api.create_listing(
            user,
            f"Item{_}",
            f"Description for Item{_}",
            random.randint(10, 500),
            category,
        )
        listings_per_user[user].append(listing_id)
        listings_per_category[category] += 1

    def check_top_category():
        max_count = max(listings_per_category.values())
        expected_top_categories = [
            cat for cat, count in listings_per_category.items() if count == max_count
        ]

        top_categories_result = api.get_top_categories(users[0])

        result_set = set(top_categories_result.split('\n'))
        expected_set = set(expected_top_categories)

        assert result_set == expected_set, f"Expected {expected_set}, got {result_set}"

    check_top_category()

    # Randomly delete listings
    for _ in range(NUM_LISTINGS // 5):
        user = random.choice(users)
        listing_id = listings_per_user[user].pop()

        category = api.get_listing(user, listing_id).split("|")[4]
        listings_per_category[category] -= 1

        api.delete_listing(user, listing_id)

        check_top_category()
