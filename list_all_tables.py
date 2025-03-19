import sqlite3

def list_all_tables(db_path="cloudshop.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()


    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Contents of table: {table_name}")

        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    conn.close()

if __name__ == "__main__":
    list_all_tables()
