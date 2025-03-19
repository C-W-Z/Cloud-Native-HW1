from datetime import datetime
from enum import Enum

class ReturnType(Enum):
    Success = 0
    Failed = 1
    User_Already_Exist = 2
    Unknown_User = 3
    Listing_Owner_Mismatch = 4
    Listing_Not_Found = 5
    Category_Not_Found = 6

class User:
    def __init__(self, username):
        self.username = username

class Listing:
    def __init__(self, ownername, title, description, price, category, created_at = None):
        self.ownername = ownername
        self.title = title
        self.description = description
        self.price = price
        if created_at:
            self.created_at = created_at
        else:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.category = category

class Category:
    def __init__(self, category_name, listing_count = 0):
        self.category_name = category_name
        self.listing_count = listing_count
