import os
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg
from psycopg import sql as pg_sql
import csv

app = Flask(__name__)
app.secret_key = "replace_with_secure_value"

DB_SETTINGS = {
    "dbname":   "imdb",
    "user":     "postgres",
    "password": "cjj89djy",
    "host":     "localhost",
    "port":     5433
}

def init_db():
    base_dir    = os.path.abspath(os.path.dirname(__file__))
    init_path   = os.path.join(base_dir, "init.sql")
    csv_path    = os.path.join(base_dir, "imdb_top_1000.csv")
    schema_path = os.path.join(base_dir, "imdbDatabase.sql")

    conn = psycopg.connect(**DB_SETTINGS)
    conn.autocommit = False
    cur = conn.cursor()

    # Step 1: Create 'movies' table
    with open(init_path, "r", encoding="utf8") as f:
        cur.execute(f.read())

    # Step 2: Read CSV and INSERT rows
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

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            flash("Username cannot be blank.", "danger")
            return redirect(url_for("add_user"))
        try:
            conn = psycopg.connect(**DB_SETTINGS)
            conn.autocommit = False
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username) VALUES (%s) RETURNING user_id;",
                (username,)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            flash(f"User '{username}' created with ID {new_id}.", "success")
            return redirect(url_for("add_user"))
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

    return render_template("add_user.html")

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
