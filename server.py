from flask import Flask, redirect, request, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
import os, requests
from pprint import pformat

from model import connect_to_db, db, Recipe, Ingredient, Recipe_Ingredient, User, Bookmark

app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
# app.jinja_env.auto_reload = True 

#Required to use Flask sessions and the debug toolbar
app.secret_key = "adobo"

API_KEY = os.environ['SPOONACULAR_KEY']

@app.route('/')
def begin_homepage():
    """Homepage"""
    # put a recipe into the db by hand
    # query database for a recipe 
    # create a template to show the recipe 
    # pass recipe info down to template 
    return render_template('homepage.html')


@app.route('/new-user', methods=['GET'])
def show_new_user_form():
    """Shows a form to add a new user's information"""

    return render_template('new-user.html')

@app.route('/new_user', methods=['POST'])
def enter_new_user_data():
    """Enters new user information"""

    email = request.form.get("email")
    password = request.form.get("password")

    user_in_db = User.query.filter_by(email=email).first()

    if not user_in_db:
        user = User(email=email,
                    password=password)

        db.session.add(user)
        db.session.commit()

    return redirect('/')

@app.route('/ingredients')
def show_ingredients_form():
    """search recipes by entering ingredients in form"""

    return render_template('search-form.html')

@app.route('/recipes/<recipe_id>')
def show_recipe_details(recipe_id):

    rcp_id = recipe_id
    
    headers = ({
        "x-rapidapi-host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        "x-rapidapi-key": API_KEY
        });

    url = 'https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{}/information'.format(recipe_id)
    print(url)

    payload = {'apiKey': API_KEY,
               'id': rcp_id}

    response = requests.get(url,
                            params=payload,
                            headers=headers)

    data = response.json()

    return render_template('recipe-details.html',
                           data=data,
                           id=rcp_id)


@app.route('/ingredients/search')
def search_recipes():
    """Search recipes by ingredient"""

    ingredients = (request.args.get('ingredients')).title()
    num_recipes =request.args.get('num_recipes')
    
    headers = ({
        "x-rapidapi-host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
        "x-rapidapi-key": API_KEY
        })
    
    url = 'https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByIngredients'
    

    payload = {'apiKey': API_KEY,
               'ingredients': ingredients,
               'num_recipes': num_recipes}

    response = requests.get(url, 
                            params=payload, 
                            headers=headers)

    data = response.json()
    
    for recipe in data:
        recipe_id = recipe['id']
        recipe_title = recipe['title']

    return render_template('search-results.html',
                            data=data,
                            ingredients=ingredients,
                            results=data,
                            recipe_id=recipe_id,
                            recipe_title=recipe_title)


@app.route('/recipes')
def recipe_list():
    """Show a list of user recipes"""

    recipes = Recipe.query.all()
    return render_template('recipe_list.html',
                            recipes=recipes)

@app.route('/enter-recipe', methods=['GET'])
def enter_recipe():
    """Shows a form for a user to enter a recipe"""

    return render_template('enter_recipe.html')

@app.route('/enter-recipe', methods=['POST'])
def recipe_entered():
    """Adds a recipe that a user entered into the recipe directory"""

    recipe_name = request.form.get('recipe_name')
    directions = request.form.get('directions')
    prep_time = request.form.get('prep-time')
    cook_time = request.form.get('cook-time')
    cuisine = request.form.get('cuisine')

    recipe = Recipe(recipe_name=recipe_name,
                    directions=directions,
                    prep_time=prep_time,
                    cook_time=cook_time,
                    cuisine=cuisine)

    db.session.add(recipe)
    db.session.commit()

    return redirect('/')

if __name__ == "__main__":
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)
    # DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    # DebugToolbarExtension(app)
    app.run(host="0.0.0.0")

#ignore me
#<a href="/recipes/{{ data[0]['id'] }}">