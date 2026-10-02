DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    full_name TEXT NOT NULL,
    bio TEXT NOT NULL DEFAULT "",
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS parts;
CREATE TABLE parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    pn TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    internal_revision INTEGER NOT NULL DEFAULT 1,
    internal_eco TEXT NOT NULL,
    customer_revision TEXT,
    customer_eco TEXT,
    type TEXT NOT NULL, /* "manufactured", "purchased", "document", "level" */
    unit TEXT,
    manufacturer TEXT,
    mpn TEXT,
    bom TEXT
);

DROP TABLE IF EXISTS eco;
CREATE TABLE eco (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    eco TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT "pending", /* "pending", "released" */
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    released_at DATETIME,
    FOREIGN KEY (eco) REFERENCES parts(internal_eco)
);

DROP TABLE IF EXISTS changes;
CREATE TABLE changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    eco TEXT NOT NULL,
    type TEXT NOT NULL,
    object_changed TEXT NOT NULL,
    value_changed TEXT NOT NULL,
    original_value TEXT,
    new_value TEXT NOT NULL,
    FOREIGN KEY (eco) REFERENCES eco(eco)
);

DROP TABLE IF EXISTS bom;
CREATE TABLE bom (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    bom TEXT NOT NULL,
    component_pn TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (bom) REFERENCES parts(bom),
    FOREIGN KEY (component_pn) REFERENCES parts(pn)
);
