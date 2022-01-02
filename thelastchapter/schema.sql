DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS list_names;
DROP TABLE IF EXISTS book_lists;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL DEFAULT Anonymous,
    password TEXT NOT NULL
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    image TEXT NOT NULL,
    published TEXT,
    genre TEXT NOT NULL,
    info TEXT,
    lang TEXT NOT NULL,
    pages INTEGER,
    price TEXT NOT NULL
);

CREATE TABLE list_names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE book_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY (list_id) REFERENCES list_names (id),
    FOREIGN KEY (book_id) REFERENCES books (id)
);