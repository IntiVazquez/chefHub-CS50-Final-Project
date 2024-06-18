from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql
import requests

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure the MySQL connection
connection = pymysql.connect(
    host = 'localhost',
    user = 'root',
    password = '****************', # Enter your MySQL password
    database = 'chefhub',
    cursorclass = pymysql.cursors.DictCursor)

# API Key
apiKey = "05e0b910b0ed4e45b03360af054fa73c"

# Index Page
@app.route("/", methods=["GET", "POST"])    
def index():
    # Retrieve API data
    url = "https://api.spoonacular.com/recipes/random?apiKey=" + apiKey + "&number=3"
    recipes = requests.get(url)
    dataRecipes = recipes.json()
    
    # Send data to the index page
    return render_template("index.html", recipes=dataRecipes["recipes"])


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        recipe_name = request.form.get("recipe_name")
        # Retrieve API data
        url = "https://api.spoonacular.com/recipes/complexSearch?apiKey=" + apiKey + "&query=" + recipe_name + "&number=6"
        recipes = requests.get(url)
        dataRecipes = recipes.json()
        return render_template("search.html", recipes = dataRecipes['results'])
    else:
        return render_template("search.html")


@app.route("/recipe/<int:id>", methods=["GET", "POST"])
def recipe(id):
    # Retrieve API data
    url = "https://api.spoonacular.com/recipes/" + str(id) + "/information?apiKey=" + apiKey
    recipe = requests.get(url)
    dataRecipe = recipe.json()

    if len(session):
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM favorites WHERE user_id = %s AND recipe_id = %s", (session["user_id"], str(id)))
            if cur.rowcount == 1:
                favorite = True
            else:
                favorite = False
            if request.method == "POST":
                print("stop")
                if favorite:
                    cur.execute("DELETE FROM favorites WHERE user_id = %s AND recipe_id = %s", (session["user_id"], id))
                else:
                    cur.execute("INSERT INTO favorites (user_id, recipe_id, recipe_name, recipe_img) VALUES (%s, %s, %s, %s)", (session["user_id"], id, dataRecipe['title'], dataRecipe['image']))
                connection.commit()
                return redirect(url_for("recipe", id=id))
            else:
                return render_template("recipe.html", recipe=dataRecipe, favorite=favorite)
        
    else:
        return render_template("recipe.html", recipe=dataRecipe)
        

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if not request.form.get("username"):
            flash("Must provide a username")
            return render_template("register.html")
        
        elif len(request.form.get("username")) > 30:
            flash("Username must be shorter than 30 characters")
            return render_template("register.html")
        
        elif not request.form.get("password"):
            flash("Must provide a password")
            return render_template("register.html")
        
        elif not request.form.get("confirmation"):
            flash("Must provide a confirmation")
            return render_template("register.html")
        
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Password and Password Confirmation must be the same")
            return render_template("register.html")
        
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", request.form.get("username"))

            if cur.rowcount != 0:
                flash("Username alredy exists")
                return render_template("register.html")
            
            cur.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (request.form.get("username"), generate_password_hash(request.form.get("password"))))
            connection.commit()

            return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            flash("Must provide a username")
            return render_template("login.html")
        
        elif not request.form.get("password"):
            flash("Must provide a password")
            return render_template("login.html")
        
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", request.form.get("username"))

            rows = cur.fetchall()

            if cur.rowcount  != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                flash("invalid username and/or password")
                return render_template("login.html")
            
            session["user_id"] = rows[0]["id"]

            return redirect("/")
    
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/favorites")
def favorites():
    if len(session):
        with connection.cursor() as cur:
            cur.execute("SELECT recipe_id, recipe_name, recipe_img FROM favorites WHERE user_id = %s", session["user_id"])

            favorites_list = cur.fetchall()

            return render_template("favorites.html", favorites_list=favorites_list)
    else:
        return redirect("/")


if __name__=='__main__':
    app.run(debug=True)