import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg
import csv
from datetime import date

app = Flask(__name__)
app.secret_key = "api_key"  # doesnt matter if u change this

DB_SETTINGS = {
    "dbname":   "INSERT dbname HERE", # INSERT DBNAME
    "user":     "postgres", # INSERT USER
    "password": "INSERT PASSWORD HERE", # INSERT PASSWORD
    "host":     "localhost", # propably no need to change this
    "port":     5432 # INSERT PORT (5432 is default i think)
}

def init_db():
    #create movies table, load CSV, drop columns, create other tables from .sql files
    # make sure paths are correct
    base_dir    = os.path.abspath(os.path.dirname(__file__))
    init_path   = os.path.join(base_dir, "init.sql")
    csv_path    = os.path.join(base_dir, "imdb_top_1000.csv")
    schema_path = os.path.join(base_dir, "imdbDatabase.sql")

    conn = psycopg.connect(**DB_SETTINGS)
    conn.autocommit = False
    cur = conn.cursor()

    # Step 1: Create 'movies' table from init.sql
    with open(init_path, "r", encoding="utf8") as f:
        cur.execute(f.read())

    # Step 2: Load csv
    tuples = []
    with open(csv_path, "r", encoding="utf8") as f:
        reader = csv.reader(f)
        original_header = next(reader)
        header = [col.strip().lower() for col in original_header]

        f.seek(0)
        dict_reader = csv.DictReader(f, fieldnames=header)
        next(dict_reader)

        for row in dict_reader:
            released_year = int(row["released_year"]) if row["released_year"].strip() else None
            imdb_rating   = float(row["imdb_rating"])   if row["imdb_rating"].strip()   else None
            meta_score    = int(row["meta_score"])      if row["meta_score"].strip()      else None
            no_of_votes   = int(row["no_of_votes"])     if row["no_of_votes"].strip()     else None

            gross_raw = row["gross"].strip()
            gross_val = gross_raw.replace(",", "") if gross_raw else None

            tuples.append((
                row["poster_link"].strip() or None,
                row["series_title"].strip() or None,
                released_year,
                row["certificate"].strip() or None,
                row["runtime"].strip() or None,
                row["genre"].strip() or None,
                imdb_rating,
                row["overview"].strip() or None,
                meta_score,
                row["director"].strip() or None,
                row["star1"].strip() or None,
                row["star2"].strip() or None,
                row["star3"].strip() or None,
                row["star4"].strip() or None,
                no_of_votes,
                gross_val
            ))
    # to insert the dataset we created the tabæes with the exact columns, we just drop them later in imdbDatabase.sql
    insert_sql = """
        INSERT INTO movies (
          poster_link,
          series_title,
          released_year,
          certificate,
          runtime,
          genre,
          imdb_rating,
          overview,
          meta_score,
          director,
          star1,
          star2,
          star3,
          star4,
          no_of_votes,
          gross
        )
        VALUES (
          %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
          %s, %s, %s, %s, %s, %s
        );
    """
    cur.executemany(insert_sql, tuples)
    conn.commit()

    # Step 3: Drop columns and create other tables
    with open(schema_path, "r", encoding="utf8") as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()

# Initialize DB on startup
init_db()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    """
    GET: show the form to create a new user.
    POST: insert into users(username) in database, then redirect to /start_game?user_id=<new_id>
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            flash("Username cannot be blank.", "danger")
            return redirect(url_for("add_user"))
        if not re.fullmatch(r"\w{3,12}", username):
            flash("Username must be inbetween 3-12 characters, with no special characters.", "danger")
            return redirect(url_for("add_user"))
        try:
            conn = psycopg.connect(**DB_SETTINGS)
            conn.autocommit = False
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username) VALUES (%s) RETURNING user_id;",
                (username,)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            # Redirect to start_game with this new user_id
            return redirect(url_for("start_game", user_id=user_id))

        except psycopg.errors.UniqueViolation:
            conn.rollback()
            cur.close()
            conn.close()
            flash(f"Username '{username}' is already taken. Try another.", "warning")
            return redirect(url_for("add_user"))

        except Exception as e:
            if conn:
                conn.rollback()
                cur.close()
                conn.close()
            flash(f"Error creating user: {e}", "danger")
            return redirect(url_for("add_user"))

    # GET: show form
    return render_template("add_user.html")


@app.route("/start_game")
def start_game():
    """
    Expects user_id=<id> in query string. Creates a new game_session,
    picks 10 random movie_ids, stores them (and score=0) in session,
    then redirects to template/game/<game_id>/0
    """
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        flash("No user specified.", "danger")
        return redirect(url_for("home"))

    # 1) Insert new game_session only 1 difficulty implememted
    conn = psycopg.connect(**DB_SETTINGS)
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO game_session (user_id, difficulty) VALUES (%s, %s) RETURNING game_id;",
        (user_id, 1)
    )
    game_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # 2) Pick 10 random movie_ids from movies table
    conn = psycopg.connect(**DB_SETTINGS)
    cur = conn.cursor()
    cur.execute("SELECT movie_id FROM movies ORDER BY random() LIMIT 10;")
    movie_ids = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    # 3) Store list + initial score=0 in session under key f"game_{game_id}"
    #session[f"game_{game_id}_list"] = movie_ids
    #session[f"game_{game_id}_score"] = 0

     # 3) Remember this user_id in session so “Play Again” knows who to reuse
    session["current_user_id"] = user_id
    session[f"game_{game_id}_list"] = movie_ids
    session[f"game_{game_id}_score"] = 0

    # Redirect to first question (index 0)
    return redirect(url_for("play_game", game_id=game_id, idx=0))


@app.route("/game/<int:game_id>/<int:idx>", methods=["GET", "POST"])
def play_game(game_id, idx):
    movie_list_key = f"game_{game_id}_list"
    score_key      = f"game_{game_id}_score"

    # 10 rounds in a game
    if idx >= 10:
        return redirect(url_for("game_over", game_id=game_id))

    movie_list = session.get(movie_list_key)
    if not movie_list or len(movie_list) != 10:
        flash("Game session not found or expired.", "danger")
        return redirect(url_for("home"))

    movie_id = movie_list[idx]

    # Handle POST: guess or skip
    if request.method == "POST":
        user_guess = request.form.get("guess", "").strip()

        # Fetch the real title so we can compare
        conn = psycopg.connect(**DB_SETTINGS)
        cur = conn.cursor()
        cur.execute("SELECT series_title FROM movies WHERE movie_id = %s;", (movie_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        real_title = row[0] if row else ""

        if "skip" in request.form:
            # Move to next movie without changing score
            return redirect(url_for("play_game", game_id=game_id, idx=idx + 1))
        pattern = re.sub(r'\W+', '', real_title.strip().lower())
        guess_clean = re.sub(r'\W+', '', user_guess.strip().lower())
        if pattern == guess_clean:
            session[score_key] = session.get(score_key, 0) + 1
            flash("Correct!", "success")
        else:
            flash(f"Incorrect. The correct title was '{real_title}'.", "danger")

        return redirect(url_for("play_game", game_id=game_id, idx=idx + 1))

    # GET: fetch only the columns that still exist
    conn = psycopg.connect(**DB_SETTINGS)
    cur = conn.cursor()
    cur.execute("""
        SELECT
          released_year,
          genre,
          imdb_rating,
          overview,
          director,
          star1,
          star2,
          no_of_votes,
          gross
        FROM movies
        WHERE movie_id = %s
    """, (movie_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        flash("Movie not found.", "danger")
        return redirect(url_for("home"))

    (released_year, genre, imdb_rating, overview,
     director, star1, star2, no_of_votes, gross) = row

    return render_template("game.html",
                           game_id=game_id,
                           idx=idx,
                           released_year=released_year,
                           genre=genre,
                           imdb_rating=imdb_rating,
                           overview=overview,
                           director=director,
                           star1=star1,
                           star2=star2,
                           no_of_votes=no_of_votes,
                           gross=gross)



@app.route("/game_over/<int:game_id>")
def game_over(game_id):
    score_key      = f"game_{game_id}_score"
    movie_list_key = f"game_{game_id}_list"
    score          = session.get(score_key, 0)

    # Record the final score into the `record` table (existing logic):
    conn = psycopg.connect(**DB_SETTINGS)
    cur = conn.cursor()
    # Look up user_id and difficulty (in case you need it elsewhere)
    cur.execute("SELECT user_id, difficulty FROM game_session WHERE game_id = %s;", (game_id,))
    row = cur.fetchone()
    if row:
        user_id, difficulty = row
        cur.execute(
            "INSERT INTO record (user_id, difficulty, date, points) VALUES (%s, %s, %s, %s);",
            (user_id, difficulty, date.today(), score)
        )
        conn.commit()
    cur.close()
    conn.close()

    # Clear out session data for this game
    session.pop(score_key, None)
    session.pop(movie_list_key, None)

    # Retrieve the user_id from session (set in start_game)
    current_user_id = session.get("current_user_id")

    return render_template("game_over.html",
                           score=score,
                           user_id=current_user_id)



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
