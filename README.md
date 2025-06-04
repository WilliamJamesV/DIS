#Movie Guessr

This is an unfinished version of a movie guessor game. 
The database is the top 1000 movies from imdb, which can be found in the .csv.

To run the program, change the values in app.py DB_SETTINGS to match your postgres database. 

Below is a checklist on how to run the program:

* Make sure python 3.x is installed
* Make sure to have a running local PostgreSQL server - change values in app.py 
* Install requirements; run in terminal: pip3 install -r requirements.txt
* To run go to the IMDB directory and run: python3 app.py


The app is now running on http://127.0.0.1:5000/



SELECT u.*,r.*
FROM users AS u
JOIN record AS r
  ON r.user_id = u.user_id
ORDER BY u.username, r.date;

*** record library is not implemented ***
