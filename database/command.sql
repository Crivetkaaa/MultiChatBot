CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_secret TEXT
);

CREATE TABLE IF NOT EXISTS vk_users (
    user_id INTEGER REFERENCES users(id),
    vk_id INTEGER,
    user_secret TEXT
);

CREATE TABLE IF NOT EXISTS tg_users (
    user_id INTEGER REFERENCES users(id),
    tg_id INTEGER,
    user_secret TEXT
);
