import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__, static_url_path='/static')

@app.route('/index')
def index():
   # return 'Hello, World!'
    return render_template("index.html")

# MongoDB connection setup

client = MongoClient('mongodb+srv://Ritika11:L2TiqArOQW5JPReH@cluster0.iwjd02g.mongodb.net/')
db = client['fashion']
male_collection = db['men']
female_collection = db['women']
collection_users = db['users']

@app.route('/mywardrobe/<gender>')
def mywardrobe(gender):
    # Select the appropriate collection based on gender
    collection = male_collection if gender == 'male' else female_collection

    # Fetch data from the selected MongoDB collection based on gender
    data = list(collection.find().limit(100))
    
     # Separate items into Topwear, Bottomwear, and Footwear
    # Separate items into Topwear, Bottomwear, and Footwear
    topwear_data = [item for item in data if item.get('masterCategory') == 'Apparel' and item.get('subCategory') == 'Topwear'][:5]
    bottomwear_data = [item for item in data if item.get('masterCategory') == 'Apparel' and item.get('subCategory') == 'Bottomwear'][:5]
    footwear_data = [item for item in data if item.get('masterCategory') == 'Footwear'][:5]

    return render_template('mywardrobe.html', topwear_data=topwear_data, bottomwear_data=bottomwear_data, footwear_data=footwear_data, gender=gender)
# @app.route('/mywardrobe/<gender>/<int:topwear_items>/<int:bottomwear_items>/<int:footwear_items>')
# def mywardrobe(gender, topwear_items, bottomwear_items, footwear_items):
#     # Select the appropriate collection based on gender
#     collection = male_collection if gender == 'Male' else female_collection

#     # Fetch data from the selected MongoDB collection based on gender
#     data = list(collection.find().limit(100))

#     # Separate items into Topwear, Bottomwear, and Footwear
#     topwear_data = [item for item in data if item.get('masterCategory') == 'Apparel' and item.get('subCategory') == 'Topwear'][:topwear_items]
#     bottomwear_data = [item for item in data if item.get('masterCategory') == 'Apparel' and item.get('subCategory') == 'Bottomwear'][:bottomwear_items]
#     footwear_data = [item for item in data if item.get('masterCategory') == 'Footwear'][:footwear_items]

#     return render_template('mywardrobe.html', topwear_data=topwear_data, bottomwear_data=bottomwear_data, footwear_data=footwear_data, gender=gender, topwear_items=topwear_items, bottomwear_items=bottomwear_items, footwear_items=footwear_items)
  

# Signup route
@app.route('/signup', methods=['GET','POST'])
def signup():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')

         # Select the collection based on gender
        collection_users = db['men'] if gender == 'male' else db['women']
        
        # Check if the username already exists
        if collection_users.find_one({'email': email}):
            return 'Email already exists. Please choose a different one.'

        # Insert the new user into the corresponding collection
        collection_users.insert_one({'email': email, 'password': password, 'gender': gender})

        # Redirect to the signin page after successful signup
        return redirect(url_for('signin'))
    return render_template('signup.html')
# Signin route
@app.route('/signin',methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Look for the user in both men and women collections
        men_user = db['men'].find_one({'email': email, 'password': password})
        women_user = db['women'].find_one({'email': email, 'password': password})

        if men_user or women_user:
            # Redirect to the mywardrobe page with the user's gender
            gender = men_user['gender'] if men_user else women_user['gender']
            return redirect(url_for('mywardrobe', gender=gender))
        else:
            return 'Invalid email or password. Please try again.'
    return render_template('signin.html')


@app.route('/contact')
def contact():
   # return 'Hello, World!'
    return render_template("contact.html")

@app.route('/about')
def about():
   # return 'Hello, World!'
    return render_template("about.html")

@app.route('/trends')
def trends():
   # return 'Hello, World!'
    return render_template("trends.html")

@app.route('/occasion')
def occasion():
   # return 'Hello, World!'
    return render_template("occasion.html")



if __name__ == "__main__":
    app.run(debug=True, port=5500)






