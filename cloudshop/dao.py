import sqlite3
from cloudshop.models import ReturnType, User, Listing, Category

class Database:
    def __init__(self, db_path="cloudshop.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # 3 tables：users, categories, listings
            self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT UNIQUE NOT NULL,
                listing_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                category_name INTEGER NOT NULL,
                ownername TEXT NOT NULL,
                FOREIGN KEY (category_name) REFERENCES categories(category_name)
                FOREIGN KEY (ownername) REFERENCES users(username)
            );
            """)

            # setting listings ID starts from 100001
            self.conn.execute("INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES ('listings', 100000)")

    def add_user(self, user: User) -> ReturnType:
        try:
            with self.conn:
                self.conn.execute("INSERT INTO users (username) VALUES (?)", (user.username.lower(),))
            return ReturnType.Success
        except sqlite3.IntegrityError:
            return ReturnType.User_Already_Exist

    def check_user_exist(self, username: str) -> ReturnType:
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username.lower(),))
        user = cur.fetchone()
        if not user:
            return ReturnType.Unknown_User
        return ReturnType.User_Already_Exist

    def add_category(self, category: Category) -> ReturnType:
        try:
            with self.conn:
                cur = self.conn.cursor()
                cur.execute("INSERT INTO categories (category_name, listing_count) VALUES (?, ?)",
                            (category.category_name, category.listing_count))
            # return category id
            return ReturnType.Success
        except sqlite3.IntegrityError:
            return ReturnType.Failed

    def add_listing(self, listing: Listing) -> tuple[ReturnType, int]:
        if self.check_user_exist(listing.ownername) == ReturnType.Unknown_User:
            return (ReturnType.Unknown_User, 0)

        # find category
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM categories WHERE category_name = ?", (listing.category,))
        category = cur.fetchone()

        if not category:
            # category not exist, try create
            ret = self.add_category(
                Category(
                    category_name=listing.category,
                    listing_count=0
                )
            )
            if ret == ReturnType.Failed:
                return (ReturnType.Failed, 0)

        with self.conn:
            cur.execute("""
                INSERT INTO listings (title, description, price, created_at, category_name, ownername)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (listing.title, listing.description, listing.price, listing.created_at, listing.category, listing.ownername.lower()))
            # update listing count of the category
            self.conn.execute("""
                UPDATE categories SET listing_count = listing_count + 1 WHERE category_name = ?
            """, (listing.category,))

        # return listing id
        return (ReturnType.Success, cur.lastrowid)

    def get_listing(self, username, listing_id) -> tuple[ReturnType, Listing | None]:
        if self.check_user_exist(username) == ReturnType.Unknown_User:
            return (ReturnType.Unknown_User, None)

        cur = self.conn.cursor()
        cur.execute("""
            SELECT listings.ownername, listings.title, listings.description, listings.price, listings.created_at, listings.category_name
            FROM listings
            WHERE listings.id = ?
        """, (listing_id,))
        result = cur.fetchone()

        if not result:
            return (ReturnType.Listing_Not_Found, None)

        listing = Listing(
            ownername=result[0],
            title=result[1],
            description=result[2],
            price=result[3],
            created_at=result[4],
            category=result[5]
        )

        return (ReturnType.Success, listing)

    def delete_listing(self, ownername: str, listing_id: int) -> ReturnType:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT listings.category_name, listings.ownername FROM listings
            WHERE listings.id = ?
        """, (listing_id,))
        listing = cur.fetchone()

        if not listing:
            return ReturnType.Listing_Not_Found

        if listing[1] != ownername:
            return ReturnType.Listing_Owner_Mismatch

        with self.conn:
            self.conn.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
            # update listing count of the category
            self.conn.execute("""
                UPDATE categories SET listing_count = listing_count - 1 WHERE category_name = ?
            """, (listing[0],))

        return ReturnType.Success

    def get_category_listings(self, username: str, category_name: str) -> tuple[ReturnType, list[Listing]]:
        if self.check_user_exist(username) == ReturnType.Unknown_User:
            return (ReturnType.Unknown_User, [])

        # test if category exist
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id FROM categories WHERE category_name = ?
        """, (category_name,))
        category = cur.fetchone()
        if not category:
            return (ReturnType.Category_Not_Found, [])

        # get all listings，ordered by created_at in descending order
        cur.execute("""
            SELECT listings.ownername, listings.title, listings.description, listings.price, listings.created_at
            FROM listings
            WHERE category_name = ?
            ORDER BY created_at DESC
        """, (category_name,))
        results = cur.fetchall()

        listings = []
        for l in results:
            listings.append(
                Listing(
                    ownername=l[0],
                    title=l[1],
                    description=l[2],
                    price=l[3],
                    category=category_name,
                    created_at=l[4]
                )
            )

        return (ReturnType.Success, listings)

    def get_top_categories(self, username: str) -> tuple[ReturnType, list[Category]]:
        if self.check_user_exist(username) == ReturnType.Unknown_User:
            return (ReturnType.Unknown_User, [])

        cur = self.conn.cursor()
        cur.execute("""
            SELECT category_name, listing_count
            FROM categories
            WHERE listing_count = (
                SELECT MAX(listing_count)
                FROM categories
            )
        """)
        results = cur.fetchall()

        top_categories = []
        for c in results:
            top_categories.append(
                Category(
                    category_name=c[0],
                    listing_count=c[1]
                )
            )

        return (ReturnType.Success, top_categories)
