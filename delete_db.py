import os

if __name__ == "__main__":
    db_file = 'cloudshop.db'
    if os.path.exists(db_file):
        os.remove(db_file)
