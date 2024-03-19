import sqlite3 as sql
from typing import Any
from functools import cache
import difflib

class UnsupportedAccess(ValueError):
    pass;

class Neighbor:
    # In previous versions (2.0-3.*), Neighbor objects held a discord ID and accessed a .txt file
    #   for each operation to retrieve or update info.
    # 
    # In 4.0 and onward, the Neighbor holds a discord ID which links to an sql database.
    #   Conveniently, if a Neighbor's info is not found in the sql database,
    #   The old .txt files will also be searched to recover the data. Making the transition seemless.
    #
    # 4.0+ also includes methods that overload the '.' operator but it is
    #   backwards compatible with the previous methods of accessing Neighbor data.
    #  
    # This makes life easier and code cleaner in some cases: 
    #       3.*: neighbor_object.get_level() 
    #       4.0: neighbor_object.level
    #   Both will work and both access the database
    #   to retrieve the latest info available.
    #

    def __init__(self, id: int = 0, link = True):
        self.id = id;
        
    @cache
    def get_xp_by_level_recursive(level: int) -> int:
        if (level < 1):
            raise ValueError("Level cannot be lower than 1");
        if level == 1:
            return 201;
        return Neighbor.get_xp_by_level(level - 1) + int(level ** 2.5) + level + 200;

        
    @cache
    def get_level_by_xp(xp: int) -> int:
        if (xp < 0):
            raise ValueError("XP cannot be lower than 0");
        c = 1;
        while (Neighbor.get_xp_by_level(c) <= xp):
            c += 1;
        return c-1;
        
    @property
    def xp(self):
        with sql.connect("players.db") as db:
            cursor = db.cursor();
            get_xp = "SELECT n.XP FROM Neighbors n WHERE n.ID = ?;";
            cursor.execute(get_xp, (self.id,));
            result = cursor.fetchone();
            return result[0] if result else 0;
        
    @xp.setter
    def xp(self, xp):
        with sql.connect("players.db") as db:
            cursor = db.cursor();
            update_xp = "UPDATE Neighbors SET XP = ? WHERE ID = ?;"
            cursor.execute(update_xp, (xp, self.id));
            db.commit();
        
    @property
    def level(self):
        return Neighbor.get_level_by_xp(self.xp);
    
    @level.setter
    def level(self, level):
        raise UnsupportedAccess("Cannot directly set Neighbor level.");
    
    @property
    def family(self):
        with sql.connect("players.db") as db:
            cursor = db.cursor();
            get_xp = "SELECT n.FAMILY FROM Neighbors n WHERE n.ID = ?;";
            cursor.execute(get_xp, (self.id,));
            result = cursor.fetchone();
            return result[0] if result else 0;
    
    @family.setter
    def family(self, family):
        with sql.connect("players.db") as db:
            cursor = db.cursor();
            update_family = "UPDATE Neighbors SET FAMILY = ? WHERE ID = ?;"
            cursor.execute(update_family, (family, self.id));
            db.commit();
    
    @property
    def inventory(self):
        with sql.connect("players.db") as db:
            cursor = db.cursor();
            get_items = "SELECT i.NAME from Items i WHERE i.NeighborID = ?;";
            get_attributes = "SELECT a.NAME, a.VALUE from Values v WHERE v.ValueID = ?;";
            cursor.execute(get_items, (self.id,));
            
    
    def __getattribute__(self, __name: str) -> Any:
        neighbors = sql.connect("neighbors.db");
        
        neighbors.execute()
        
        neighbors.close();
        
    def __pull(self):
        """
        A Neighbor's info is pulled from its respesctive data file by searching for its ID in the file and decoding that line of text.
        """
        neighbor = None;
        with open(self.appropriate_file(), "r") as fNeighbors:
            lines = fNeighbors.readlines()
            for line in lines:
                neighbor = Neighbor.decode(line[:-2]);
                if neighbor.ID == self.ID:
                    if neighbor.family == self.family or (neighbor.family == 0 and self.family == 647883751853916162):
                        self.copy(neighbor);
                        break;
        if self.family == "0":
            raise ValueError("Family can't be 0");

        if neighbor is None or not neighbor.ID == self.ID: 
            self.XP = 0;
            self.legacyXP = 0;
            self.inventory = [];
        
    def __push(self):
        """
        A Neighbor's info is pushed to its respective data file by searching for and replacing its line using encode.
        """
        neighbors_to_write = [];
        neighbors_to_write.append(self);
        with open(self.appropriate_file(), "r") as fNeighbors:
            lines = fNeighbors.readlines();
            for line in lines:
                neighbor = Neighbor.decode(line[:-2]);
                if neighbor.ID == self.ID and ((neighbor.family == self.family) or (neighbor.family == 0 and self.family == 647883751853916162)):
                    continue;
                else:
                    neighbors_to_write.append(neighbor);
        with open(self.appropriate_file(), "w") as fNeighbors:
            for neighbor in neighbors_to_write:
                fNeighbors.write(neighbor.encode() + "\n");
    
class Item:
    def __init__(self, name: str, type: str, expiration: int, **values):
        self.name = name;
        self.type = type;
        self.expiration = int(expiration);
        self.values = {} if values is None else values;

    def __str__(self):
        if self.expiration == -1:
            res = f"{self.name}; expires never... probably";
        else:
            res = f"{self.name}; expires in {timedelta(seconds=round(self.expiration - time.time()))}";
        # res = self.name + "self.type + "* [expires in: " + str(timedelta(seconds=round(self.expiration - time.time()))) + "]";
        return res;
    
    def is_expired(self):
        return time.time() > self.expiration and self.expiration > 0;

    def encode(self):
        value_concat = "";
        for key, value in self.values.items():
            value_concat += str(key) + "=" + str(value) + ",";
        res = f"{self.name};{self.type};{str(self.expiration)};{value_concat[:-1]}";
        res.replace("'", "");
        res.replace('"', "");
        return res;

    def decode(data: str):
        fields = data.split(";")
        if len(fields) < 4 or fields[3] == "":
            res = Item(fields[0],fields[1],int(fields[2]));
        else:
            res = Item(fields[0],fields[1],int(fields[2]),**{key: str(value) for key, value in (item.split("=") for item in fields[3].split(","))});
        return res;
    
    def get_value(self, attribute: str):
        if attribute in self.values.keys():
            return self.values[attribute];
        
        alternate_candidates = [x for x in self.values.keys() if difflib.SequenceMatcher(None, x, attribute).ratio() > .5];
        raise KeyError(f"Attribute '{attribute}' not present in Item values." + ("" if not alternate_candidates else " Could you have meant: " + str(alternate_candidates) + "?"));
    
    def update_value(self, attribute: str, new_val: str):
        if attribute in self.values.keys():
            self.values[attribute] = new_val;
            return;
        
        alternate_candidates = [x for x in self.values.keys() if difflib.SequenceMatcher(None, x, attribute).ratio() > .5];
        raise KeyError(f"Attribute '{attribute}' not present in Item values." + ("" if not alternate_candidates else " Could you have meant: " + str(alternate_candidates) + "?"));

    def add_value(self, attribute: str, val: str):
        self.values[attribute] = val;
