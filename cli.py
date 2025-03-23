import sys
from cloudshop.dao import Database
from cloudshop.service import ServiceAPI
import shlex
# import time

def main():
    db = Database()
    api = ServiceAPI(db)
    for line in sys.stdin:
        tokens = shlex.split(line.strip())
        if not tokens:
            continue
        command, args = tokens[0], tokens[1:]

        if command == "REGISTER":
            print(api.register(args[0]))

        elif command == "CREATE_LISTING":
            print(api.create_listing(*args[:5]))

        elif command == "GET_LISTING":
            print(api.get_listing(*args[:2]))

        elif command == "DELETE_LISTING":
            print(api.delete_listing(*args[:2]))

        elif command == "GET_CATEGORY":
            print(api.get_category(*args[:2]))

        elif command == "GET_TOP_CATEGORY":
            print(api.get_top_categories(args[0]))

        else:
            print("Error - invalid command")

        # time.sleep(0.5)

if __name__ == "__main__":
    main()
