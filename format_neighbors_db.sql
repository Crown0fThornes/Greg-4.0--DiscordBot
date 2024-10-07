CREATE TABLE IF NOT EXISTS Neighbors (
    id INTEGER PRIMARY KEY,
    Family TEXT NOT NULL,
    xp INTEGER NOT NULL,
    legacy_xp INTEGER NOT NULL,
    peak_this_month INTEGER NOT NULL 
);

CREATE TABLE IF NOT EXISTS Items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    neighbor_id INTEGER, 
    name TEXT NOT NULL,
    FOREIGN KEY (neighbor_id) REFERENCES Neighbors(id) 
);

CREATE TABLE IF NOT EXISTS Attributes (
    attreibute_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    name TEXT NOT NULL,
    value_int INTEGER, 
    value_text TEXT,
    FOREIGN KEY (item_id) REFERENCES Items(item_id),
);

CREATE INDEX IF NOT EXISTS Neighbor_Items
ON Items (neighbor_id, name);

CREATE INDEX IF NOT EXISTS Item_Attributes
ON Attributes (item_id);