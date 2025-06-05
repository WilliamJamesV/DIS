#Movie Guessr

The database is the top 1000 movies from imdb, which can be found in the .csv.

To run the program, change the values in app.py DB_SETTINGS to match your postgres database. 

Below is a checklist on how to run the program:

* Make sure python 3.x is installed
* Make sure to have a running local PostgreSQL server - change values in app.py accordingly
* Install requirements; run in terminal: pip3 install -r requirements.txt
* To run go to the IMDB directory and run: python3 app.py

The app is now running on http://127.0.0.1:5000/

The game works like this:

When the web-app first opens you start in the home screen, where there is a single button
leading you to user creation.

In user creation you will have to decide on a username. The username cannot be empty
and it has to be between 3 and 12 characters. Once you have decided on your username
you go into the game.

In this stage you will be presented with different data about a movie, and it is your
job to guess what movie it is. Once you have submitted your guess you will continue
on to the next movie. At the top there will be a display that either says "Correct"
or "Incorrect. The correct movie was: "Movie name".

Once you have tried to guess all 10 movies you will be presented with your final score.

You then choose to either play again, where you will try and guess 10 movies again (play
the game again), or you can go back to the home screen.

If you go back to the home screen, and then create a new user, you will not be able to 
use the same username again. You have to choose a new username.

If you want to see how you did with each attempt insert the code below in the query tool
in pgAdmin and press the triangle in the tool bar that runs the script.

SELECT u.*,r.*
FROM users AS u
JOIN record AS r
  ON r.user_id = u.user_id
ORDER BY u.username, r.date;

*** record library is not implemented ***
