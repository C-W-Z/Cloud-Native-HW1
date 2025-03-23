from cloudshop.models import ReturnType, User, Listing, Category
from cloudshop.dao import Database

class ServiceAPI:
    def __init__(self, database: Database):
        self.db = database

    def register(self, username: str):
        res = self.db.add_user(User(username))
        if res == ReturnType.Success:
            return "Success"
        elif res == ReturnType.User_Already_Exist:
            return "Error - user already existing"
        else:
            return "Unknwon Error"

    def create_listing(self, ownername: str, title: str, description: str, price: str, category: str):
        res, listing_id = self.db.add_listing(Listing(ownername, title, description, price, category))
        if res == ReturnType.Success:
            return listing_id
        elif res == ReturnType.Unknown_User:
            return "Error - unknown user"
        else:
            return "Unknwon Error"

    def get_listing(self, username: str, listing_id: str):
        listing_id = int(listing_id)
        res, listing = self.db.get_listing(username, listing_id)
        if res == ReturnType.Success and listing:
            return f"{listing.title}|{listing.description}|{listing.price}|{listing.created_at}|{listing.category}|{listing.ownername}"
        elif res == ReturnType.Unknown_User:
            return "Error - unknown user"
        elif res == ReturnType.Listing_Not_Found:
            return "Error - not found"
        else:
            return "Unknwon Error"

    def delete_listing(self, username: str, listing_id: str):
        listing_id = int(listing_id)
        res = self.db.delete_listing(username, listing_id)
        if res == ReturnType.Success:
            return "Success"
        elif res == ReturnType.Listing_Not_Found:
            return "Error - listing does not exist"
        elif res == ReturnType.Listing_Owner_Mismatch:
            return "Error - listing owner mismatch"
        else:
            return "Unknwon Error"

    def get_category(self, username: str, category_name: str):
        res, listings = self.db.get_category_listings(username, category_name)
        if res == ReturnType.Success:
            ret = ""
            for i, l in enumerate(listings):
                if i > 0:
                    ret += "\n"
                ret += f"{l.title}|{l.description}|{l.price}|{l.created_at}|{l.category}|{l.ownername}"
            return ret
        elif res == ReturnType.Category_Not_Found:
            return "Error - category not found"
        elif res == ReturnType.Unknown_User:
            return "Error - unknown user"
        else:
            return "Unknwon Error"

    def get_top_categories(self, username: str):
        res, categories = self.db.get_top_categories(username)
        if res == ReturnType.Success:
            category_names = []
            for c in categories:
                category_names.append(c.category_name)
            category_names.sort()
            ret = ""
            for i, cn in enumerate(category_names):
                if i > 0:
                    ret += "\n"
                ret += cn
            return ret
        elif res == ReturnType.Unknown_User:
            return "Error - unknown user"
        else:
            return "Unknwon Error"
