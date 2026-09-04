CREATE TABLE IF NOT EXISTS vk_users (
    vk_id INTEGER,
    user_secret TEXT
);

CREATE TABLE IF NOT EXISTS tg_users (
    tg_id INTEGER,
    user_secret TEXT
);

CREATE TABLE IF NOT EXISTS mx_users (
    mx_id INTEGER,
    user_secret TEXT
);

CREATE TABLE IF NOT EXISTS p2p (
    user_secret TEXT,
    who_secret TEXT,
    chat_name TEXT,
    UNIQUE (user_secret, who_secret)
)