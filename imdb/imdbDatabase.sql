
ALTER TABLE movies
  DROP COLUMN poster_link,
  DROP COLUMN certificate,
  DROP COLUMN runtime,
  DROP COLUMN meta_score,
  DROP COLUMN star3,
  DROP COLUMN star4;

DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS game_session CASCADE;
DROP TABLE IF EXISTS record CASCADE;

CREATE TABLE users (
  user_id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  username        TEXT        NOT NULL UNIQUE,
  record_library  INTEGER[]   -- record of played games
);

CREATE TABLE game_session (
  game_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     INTEGER NOT NULL
    REFERENCES users(user_id)
    ON DELETE CASCADE,
  difficulty  INTEGER
);

CREATE TABLE record (
  record_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     INTEGER NOT NULL
    REFERENCES users(user_id)
    ON DELETE CASCADE,
  difficulty  TEXT       NOT NULL,    
  date        DATE       NOT NULL,
  points      INTEGER    NOT NULL
);
