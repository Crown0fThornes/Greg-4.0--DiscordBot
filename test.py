import sqlite3 as sql

conn = sql.connect("neighbors.db")

conn.execute(''' CREATE TABLE IF NOT EXISTS neighbors
             (ID INTEGER PRIMARY KEY AUTOINCREMENT,
             Name TEXT NOT NULL,
             DiscordID TEXT NOT NULL);''');

def insert_member(name, discord_id):
    conn.execute("INSERT INTO neighbors (Name, DiscordID) VALUES (?, ?)",
                 (name, discord_id))
    conn.commit()
    print("Neighbors added successfully")

# Example usage
insert_member("JohnDoe", "123456789");

def query_members():
    cursor = conn.execute("SELECT ID, Name, DiscordID FROM neighbors")
    for row in cursor:
        print(f"ID = {row[0]}, Name = {row[1]}, DiscordID = {row[2]}")

query_members()

conn.close();