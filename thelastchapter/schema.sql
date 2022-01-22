DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS books;
DROP INDEX IF EXISTS sort;
DROP TABLE IF EXISTS books_fts;
DROP TRIGGER IF EXISTS books_ai;
DROP TRIGGER IF EXISTS books_au;
DROP TRIGGER IF EXISTS books_ad;
DROP TABLE IF EXISTS list_names;
DROP TABLE IF EXISTS book_lists;
DROP TABLE IF EXISTS home_display;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_books;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL DEFAULT Anonymous,
    permissions TEXT DEFAULT USER,
    password TEXT NOT NULL
);

CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    image TEXT NOT NULL,
    published TEXT,
    genre TEXT NOT NULL,
    genre_id INTEGER NOT NULL,
    info TEXT,
    lang TEXT NOT NULL,
    pages INTEGER,
    isbn TEXT NOT NULL,
    stock INTEGER NOT NULL,
    price TEXT NOT NULL,
    FOREIGN KEY (genre_id) REFERENCES genres
);

CREATE INDEX sort ON books(title, id, genre_id);

CREATE VIRTUAL TABLE books_fts USING fts5(
    title,
    author,
    genre,
    isbn,
    content="books",
    content_rowid="id"
);

CREATE TRIGGER books_ai AFTER INSERT ON books
    BEGIN
        INSERT INTO books_fts (rowid, title, author, genre, isbn)
        VALUES (new.id, new.title, new.author, new.genre, new.isbn);
    END;

CREATE TRIGGER books_ad AFTER DELETE ON books
    BEGIN
        INSERT INTO books_fts (books_fts, rowid, title, author, genre, isbn)
        VALUES ('delete', old.id, old.title, old.author, old.genre, old.isbn);
    END;

CREATE TRIGGER books_au AFTER UPDATE ON books
    BEGIN
        INSERT INTO books_fts (rowid, title, author, genre, isbn)
        VALUES ('delete', old.id, old.title, old.author, old.genre, old.isbn);
        INSERT INTO books_fts (rowid, title, author, genre, isbn)
        VALUES (new.id, new.title, new.author, new.genre, new.isbn);
    END;

CREATE TABLE list_names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE book_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY (list_id) REFERENCES list_names (id),
    FOREIGN KEY (book_id) REFERENCES books (id)
);

CREATE TABLE home_display (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    FOREIGN KEY (list_id) REFERENCES list_names(id)
);

CREATE TABLE carts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (book_id) REFERENCES books (id)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE order_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (book_id) REFERENCES books (id)
);
