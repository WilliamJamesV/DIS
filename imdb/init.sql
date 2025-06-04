DROP TABLE IF EXISTS movies CASCADE;

CREATE TABLE movies (
  movie_id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  poster_link     TEXT,
  series_title    TEXT,
  released_year   INTEGER,
  certificate     TEXT,
  runtime         TEXT,
  genre           TEXT,
  imdb_rating     NUMERIC(3,1),
  overview        TEXT,
  meta_score      INTEGER,
  director        TEXT,
  star1           TEXT,
  star2           TEXT,
  star3           TEXT,
  star4           TEXT,
  no_of_votes     INTEGER,
  gross           TEXT
);