import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from flask_pymongo import PyMongo
app = Flask(__name__, static_url_path='/static')

app.config['MONGO_URI'] = 'mongodb+srv://Ritika11:L2TiqArOQW5JPReH@cluster0.iwjd02g.mongodb.net/'
mongo = PyMongo(app)


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

# Mapping of filter values to corresponding 'usage' and 'season' values
usage_mapping = {
    'casual': 'Casual',
    'ethnic': 'Ethnic',
    'formal': 'Formal',
    'party': 'Party',
    'sports': 'Sports'
}

season_mapping = {
    'fall': 'Fall',
    'spring': 'Spring',
    'summer': 'Summer',
    'winter': 'Winter'
}

@app.route('/mywardrobe/<gender>/<user_id>', methods=['GET', 'POST'])
def mywardrobe(gender, user_id):
    
    # Select the appropriate collection based on gender
    collection = male_collection if gender == 'male' else female_collection

    # Fetch data from the selected MongoDB collection based on gender
    data = list(collection.find().limit(100))
    
    # Get the page parameter from the request, default to 1 if not provided
    page = int(request.args.get('page', 1))

    # Adjust the number of items to display per page
    items_per_page = 5

    # Calculate the start and end indices for the current page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page

    # Separate items into Topwear, Bottomwear, and Footwear
    topwear_data = [item for item in data if item.get('masterCategory') == 'Apparel' and item.get('subCategory') == 'Topwear'][start_index:end_index]
    bottomwear_data = [item for item in data if item.get('masterCategory') == 'Apparel' and item.get('subCategory') == 'Bottomwear'][start_index:end_index]
    footwear_data = [item for item in data if item.get('masterCategory') == 'Footwear'][start_index:end_index]

    item = topwear_data[0] if topwear_data else None
    item = bottomwear_data[0] if bottomwear_data else None
    item = footwear_data[0] if footwear_data else None

    #fetch user information
    user_info = collection_users.find_one({'_id': ObjectId(user_id)})
    
    return render_template('mywardrobe.html', topwear_data=topwear_data, bottomwear_data=bottomwear_data, footwear_data=footwear_data, gender=gender, item=item, page=page, user_info=user_info)
    

@app.route('/load_more/<gender>/<category>')
def load_more(gender, category):
    # Select the appropriate collection based on gender
    collection = male_collection if gender == 'male' else female_collection

    # Fetch data from the selected MongoDB collection based on gender
    data = list(collection.find().limit(5000))
    
    # Get the page parameter from the request, default to 1 if not provided
    page = int(request.args.get('page', 1))

    # Adjust the number of items to display per page    
    items_per_page = 5

    # Calculate the start and end indices for the current page
    start_index = (page) * items_per_page
    end_index = start_index + items_per_page

    if category == 'topwear':
        category_data = [item for item in data if item.get('subCategory') == 'Topwear'][start_index:end_index]
    elif category == 'bottomwear':
        category_data = [item for item in data if item.get('subCategory') == 'Bottomwear'][start_index:end_index]
    elif category == 'footwear':
        category_data = [item for item in data if item.get('masterCategory') == 'Footwear'][start_index:end_index]
    else:
        return jsonify({'error': 'Invalid category'})
    
    
    response_data = {
        f'{category}_data': [
            {'id': item['id'], 'productDisplayName': item['productDisplayName']} for item in category_data
        ],
        'next_page': page + 1
    }

    # Return the JSON response
    return jsonify(response_data)

@app.route('/selected_items/<gender>', methods=['GET', 'POST'])
def selected_items(gender):
    try:
        if request.method == 'POST':
             # Get the selected item IDs from the request data
            topwear_ids = request.json.get('tids', [])
            bottomwear_ids = request.json.get('bids', [])
            footwear_ids = request.json.get('fids', []) 
        

             # Select the appropriate collection based on gender
            collection = male_collection if gender == 'male' else female_collection

            # Fetch selected items from the MongoDB collection for each category
            topwear_items = list(collection.find({'id': {'$in': topwear_ids}}))
            bottomwear_items = list(collection.find({'id': {'$in': bottomwear_ids}}))
            footwear_items = list(collection.find({'id': {'$in': footwear_ids}}))

            # Extract relevant information (id, productDisplayName) for each item
            topwear_data = [{'id': item['id'], 'productDisplayName': item['productDisplayName']} for item in topwear_items]
            bottomwear_data = [{'id': item['id'], 'productDisplayName': item['productDisplayName']} for item in bottomwear_items]
            footwear_data = [{'id': item['id'], 'productDisplayName': item['productDisplayName']} for item in footwear_items]

            print(f"Topwear items: {topwear_data}")
            print(f"Bottomwear items: {bottomwear_data}")
            print(f"Footwear items: {footwear_data}")

            response_data = {
                'topwear_items': topwear_data,
                'bottomwear_items': bottomwear_data,
                'footwear_items': footwear_data,
                'gender': gender
            }

            return jsonify(response_data)
    
    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error fetching selected items: {e}")

        # Return a JSON response indicating an error
        return jsonify({'error': 'Error fetching selected items'}), 500

    return render_template('selected_items.html',selected_items=selected_items, gender=gender)

@app.route('/toggle_like_outfit/<int:user_id>/<int:outfit_number>', methods=['POST'])
def toggle_like_outfit(user_id, outfit_number):
    try:
        # Get the MongoDB collection for liked outfits
        liked_outfits_collection = mongo.db.liked_outfits

        # Check if the outfit is already liked by the user
        existing_like = liked_outfits_collection.find_one({'user_id': user_id, 'outfit_number': outfit_number})

        if existing_like:
            # Outfit is already liked, remove the like
            liked_outfits_collection.delete_one({'_id': existing_like['_id']})
            liked = False
        else:
            # Outfit is not liked, add the like
            liked_outfits_collection.insert_one({'user_id': user_id, 'outfit_number': outfit_number})
            liked = True

        # Return a JSON response
        return jsonify({'success': True, 'liked': liked})

    except Exception as e:
        # Handle exceptions and return an appropriate error response
        return jsonify({'error': str(e)}), 500

# Function to simulate toggling the like status (replace with your actual logic)
def toggle_like_status(user_id, outfit_number):
    # TODO: Implement your actual logic to toggle the like status in your database or storage

    # For demonstration purposes, just return True if the outfit number is odd
    return outfit_number % 2 == 1


@app.route('/filtered_items/<gender>', methods=['POST'])
def filtered_items(gender):
    try:
        filters = request.json.get('filters', {})
        print(f"Received Filters: {filters}")

        # Select the appropriate collection based on gender
        collection = male_collection if gender == 'Men' else female_collection

        # Initialize response data
        response_data = {'gender': gender, 'filtered_items': {}}

        # List of master categories to filter
        master_categories = ['Topwear', 'Bottomwear']

        # Iterate through each master category
        for category in master_categories:
            # Build a query based on the filters provided in the payload
            query = {'gender': gender, 'subCategory': category}

            # Map filter values to 'usage' and include only filters with True values in the query
            usage_filters = [usage_mapping[key] for key, value in filters.items() if value and key in usage_mapping]
            if usage_filters:
                query['usage'] = {'$in': usage_filters}

            # Map filter values to 'season' and include only filters with True values in the query
            season_filters = [season_mapping[key] for key, value in filters.items() if value and key in season_mapping]
            if season_filters:
                query['season'] = {'$in': season_filters}

            # Print the query for debugging
            print(f"Query for {category}: {query}")

            # Fetch data from MongoDB based on the constructed query
            category_data = list(collection.find(query).limit(50))

            # Print the fetched data for debugging
            print(f"Fetched data for {category}: {category_data}")

            # Add data to the response
            response_data['filtered_items'][category] = [
                {'id': item['id'], 'productDisplayName': item['productDisplayName']} for item in category_data
            ]

        # Fetch data for Footwear separately
        footwear_query = {'gender': gender, 'masterCategory': 'Footwear'}
        usage_filters = [usage_mapping[key] for key, value in filters.items() if value and key in usage_mapping]
        if usage_filters:
            footwear_query['usage'] = {'$in': usage_filters}

        season_filters = [season_mapping[key] for key, value in filters.items() if value and key in season_mapping]
        if season_filters:
            footwear_query['season'] = {'$in': season_filters}

        print(f"Query for Footwear: {footwear_query}")

        footwear_data = list(collection.find(footwear_query).limit(50))
        print(f"Fetched data for Footwear: {footwear_data}")

        response_data['filtered_items']['Footwear'] = [
            {'id': item['id'], 'productDisplayName': item['productDisplayName']} for item in footwear_data
        ]

        # Print the final response data for debugging
        print(f"Final Response Data: {response_data}")

        # Return the response
        return jsonify(response_data)

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error fetching filtered items: {e}")
        # Return a JSON response indicating an error
        return jsonify({'error': 'Error fetching filtered items'}), 500

@app.route('/load_more_filtered/<gender>/<category>', methods=['POST'])
def load_more_filtered(gender, category):
    try:
        filters = request.json.get('filters', {})
        print(f"Received Filters: {filters}")

        # Select the appropriate collection based on gender
        collection = male_collection if gender == 'Men' else female_collection

        # Initialize response data
        response_data = {'gender': gender, 'filtered_items': {}}

        # Build a query based on the filters provided in the payload
        query = {'gender': gender, 'subCategory': category}

        # Map filter values to 'usage' and include only filters with True values in the query
        usage_filters = [usage_mapping[key] for key, value in filters.items() if value and key in usage_mapping]
        if usage_filters:
            query['usage'] = {'$in': usage_filters}

        # Map filter values to 'season' and include only filters with True values in the query
        season_filters = [season_mapping[key] for key, value in filters.items() if value and key in season_mapping]
        if season_filters:
            query['season'] = {'$in': season_filters}

        # Get the page parameter from the request, default to 1 if not provided
        page = int(request.args.get('page', 2))

        # Adjust the number of items to display per page    
        items_per_page = 5

        # Calculate the start and end indices for the current page
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page

        # Fetch data from MongoDB based on the constructed query
        category_data = list(collection.find(query).limit(5000))

        # Print the fetched data for debugging
        print(f"Fetched data for {category}: {category_data}")

        # Add data to the response
        response_data['filtered_items'][category] = [
            {'id': item['id'], 'productDisplayName': item['productDisplayName'], 'usage': item['usage'], 'season': item['season']} for item in category_data[start_index:end_index]
        ]

        # Print the final response data for debugging
        print(f"Final Response Data: {response_data}")

        # Return the response
        return jsonify(response_data)

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error fetching filtered items: {e}")
        # Return a JSON response indicating an error
        return jsonify({'error': 'Error fetching filtered items'}), 500

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
            user_id = men_user['_id'] if men_user else women_user['_id']
            return redirect(url_for('mywardrobe', gender=gender, user_id=user_id))
        else:
            return 'Invalid email or password. Please try again.'
    return render_template('signin.html')


@app.route('/contact')
def contact():
   # return 'Hello, World!'
    return render_template("contact.html")

@app.route('/features')
def features():
   # return 'Hello, World!'
    return render_template("features.html")

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