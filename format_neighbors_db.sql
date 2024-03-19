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

CREATE TABLE IF NOT EXISTS Values (
    item_id INTEGER,
    neighbor_id INTEGER,
    PRIMARY KEY (item_id, neighbor_id),
    name TEXT NOT NULL,
    value_int INTEGER, 
    value_text TEXT,
    FOREIGN KEY (item_id) REFERENCES Items(item_id),
    FOREIGN KEY (neighbor_id) REFERENCES Neighbors(id) 
);
