CREATE TABLE migrations (
    version INT UNIQUE,
    apply_time TIMESTAMP WITH TIME ZONE default now(),
    sql TEXT
);
