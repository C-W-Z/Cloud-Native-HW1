import sys
from models import ReturnType, User, Listing, Category
from dao import Database
import shlex
# import time

def main():
    db = Database()
    for line in sys.stdin:
        tokens = shlex.split(line.strip())
        if not tokens:
            continue
        command, args = tokens[0], tokens[1:]

        if command == "REGISTER":
            res = db.add_user(User(args[0]))
            if res == ReturnType.Success:
                print("Success")
            elif res == ReturnType.User_Already_Exist:
                print("Error - user already existing")
            else:
                print("Unknwon Error")

        elif command == "CREATE_LISTING":
            res, list_id = db.add_listing(Listing(*args[:5]))
            if res == ReturnType.Success:
                print(list_id)
            elif res == ReturnType.Unknown_User:
                print("Error - unknown user")
            else:
                print("Unknwon Error")

        elif command == "GET_LISTING":
            username, list_id = args[:2]
            list_id = int(list_id)
            res, listing = db.get_listing(username, list_id)
            if res == ReturnType.Success and listing:
                print(f"{listing.title}|{listing.description}|{listing.price}|{listing.created_at}|{listing.category}|{listing.ownername}")
            elif res == ReturnType.Unknown_User:
                print("Error - unknown user")
            elif res == ReturnType.Listing_Not_Found:
                print("Error - not found")
            else:
                print("Unknwon Error")

        elif command == "DELETE_LISTING":
            username, list_id = args[:2]
            list_id = int(list_id)
            res = db.delete_listing(username, list_id)
            if res == ReturnType.Success:
                print("Success")
            elif res == ReturnType.Listing_Not_Found:
                print("Error - listing does not exist")
            elif res == ReturnType.Listing_Owner_Mismatch:
                print("Error - listing owner mismatch")
            else:
                print("Unknwon Error")

        elif command == "GET_CATEGORY":
            res, listings = db.get_category_listings(*args[:2])
            if res == ReturnType.Success:
                for l in listings:
                    print(f"{l.title}|{l.description}|{l.price}|{l.created_at}|{l.category}|{l.ownername}")
            elif res == ReturnType.Category_Not_Found:
                print("Error - category not found")
            elif res == ReturnType.Unknown_User:
                print("Error - unknown user")
            else:
                print("Unknwon Error")

        elif command == "GET_TOP_CATEGORY":
            res, categories = db.get_top_category(args[0])
            if res == ReturnType.Success:
                category_names = []
                for c in categories:
                    category_names.append(c.category_name)
                category_names.sort()
                for cn in category_names:
                    print(cn)
            elif res == ReturnType.Unknown_User:
                print("Error - unknown user")
            else:
                print("Unknwon Error")

        else:
            print("Error - invalid command")

        # time.sleep(0.5)

if __name__ == "__main__":
    main()
