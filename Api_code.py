from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import uuid
import mysql.connector
import requests

app = Flask(__name__)

# mySQL database configurations
config = {
    'user': 'root',
    'password': 'Password111!',
    'host': 'localhost',
    'database': 'HTTP_API'
}

cnx = mysql.connector.connect(**config)

# Helper function to execute SQL queries
def execute_query(query, data=None):
    cursor = cnx.cursor()
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)

    if 'SELECT' in query.upper():
        result = cursor.fetchall()
    elif 'INSERT' in query.upper() or 'UPDATE' in query.upper() or 'DELETE' in query.upper():
        result = None
        cnx.commit()

    cursor.close()
    return result

# other helper functions:
def get_user_id():
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    # Find user id from active session database table
    sql = 'SELECT id FROM active_sessions WHERE token = %s AND expiry > NOW()'
    data = (token,)
    id = execute_query(sql, data)
    if not id:
        return None
    
    return id[0][0]

def delete_session():
    token = request.headers.get('Authorization')
    sql = 'DELETE FROM active_sessions WHERE token = %s'
    data = (token,)
    execute_query(sql, data)

# endpoint for registering a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # check if email and password were provided
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required.'}), 400
    
    # check if email is valid
    import re
    email_regex = r'^\S+@\S+\.\S+$'
    if not re.match(email_regex, data['email']):
        return jsonify({'error': 'Invalid email format.'}), 400
    
    # check if email is already registered
    sql = 'SELECT * FROM users WHERE email = %s'
    sql_data = (data['email'],)
    user_data = execute_query(sql, sql_data)
    if user_data:
        return jsonify({'error': 'Email already registered.'}), 400
    
    # check if password meets requirements
    password_regex = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[!@#?\]])\S{10,}$'
    if not re.match(password_regex, data['password']):
        return jsonify({'error': 'Password must contain at least 10 characters, one lowercase letter, one uppercase letter, and one of the following characters: !, @, #, ?, or ].'}), 400
    
    # if all checks pass, add user to database
    new_user = {
        'id': str(uuid.uuid4()),
        'email': data['email'],
        'password': data['password']
    }
    sql = 'INSERT INTO users (id, email, password) VALUES (%s, %s, %s)'
    sql_data = (new_user['id'], new_user['email'], new_user['password'])
    execute_query(sql, sql_data)
    
    return jsonify({'message': 'User registered successfully.', 'user': new_user}), 201

# endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # check if email and password were provided
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required.'}), 400
    
    # check if email is valid
    import re
    email_regex = r'^\S+@\S+\.\S+$'
    if not re.match(email_regex, data['email']):
        return jsonify({'error': 'Invalid email format.'}), 400
    
    # check if email is already registered
    sql = 'SELECT * FROM users WHERE email = %s'
    sql_data = (data['email'],)
    user_data = execute_query(sql, sql_data)
    if not user_data:
        return jsonify({'error': 'Email not registered.'}), 400
    id = user_data[0][0]
    password = user_data[0][2]
    
    # check if password meets requirements
    password_regex = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[!@#?\]])\S{10,}$'
    if not re.match(password_regex, data['password']):
        return jsonify({'error': 'Password must contain at least 10 characters, one lowercase letter, one uppercase letter, and one of the following characters: !, @, #, ?, or ].'}), 400
    
    # check if password matches for registered user
    if data['password'] != password:
        return jsonify({'error': 'Incorrect password.'}), 400
    
    # if all checks pass, create a new session token for the user
    token = str(uuid.uuid4())
    expiry = datetime.now() + timedelta(minutes=20)
    sql = 'INSERT INTO active_sessions (id, token, expiry) VALUES (%s, %s, %s)'
    sql_data = (id, token, expiry)
    execute_query(sql, sql_data)
    
    # return the session token
    return jsonify({
        'message': 'User logged in successfully',
        'token': token
        }), 200

# endpoint for logging out
@app.route('/logout', methods=['DELETE'])
def logout():
    delete_session()
    return jsonify({'message': 'User logged out successfully'}), 204


# endpoint for reading public restaurants
@app.route('/public_restaurants', methods=['GET'])
def print_public_restaurants():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid or expired token. Please quit and re-login'}), 401
    
    try:
        # Get page and page_size query parameters, default to 1 and 10 if not provided
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        # Calculate the offset for the desired page number
        offset = (page - 1) * page_size
        
        # get all public restaurants and restaurants owned by user
        sql = 'SELECT * FROM restaurants WHERE is_public = 1 ORDER BY name ASC LIMIT %s OFFSET %s'
        data = (page_size, offset)
        public_data = execute_query(sql, data)
        fields = ['restaurant_id', 'name', 'address', 'chef\'s special', 'owner', 'tag', 'public (1) or private (0)']
        public_res = [dict(zip(fields, values)) for values in public_data]

        return jsonify({'public restaurants': public_res}), 200
    except:
        return jsonify({'error': 'Invalid parameters for pagination'}), 400
    
# endpoint for reading user-created restaurants
@app.route('/user_restaurants', methods=['GET'])
def print_user_restaurants():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid or expired token. Please quit and re-login'}), 401
    
    try:
        # Get page and page_size query parameters, default to 1 and 10 if not provided
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        # Calculate the offset for the desired page number
        offset = (page - 1) * page_size
        
        # get all public restaurants and restaurants owned by user
        sql = 'SELECT * FROM restaurants WHERE owner = %s ORDER BY name ASC LIMIT %s OFFSET %s'
        data = (user_id, page_size, offset)
        user_data = execute_query(sql, data)
        fields = ['restaurant_id', 'name', 'address', 'chef\'s special', 'owner', 'tag', 'public (1) or private (0)']
        user_res = [dict(zip(fields, values)) for values in user_data]

        return jsonify({'your restaurants': user_res}), 200
    except:
        return jsonify({'error': 'Invalid parameters for pagination'}), 400
    
# endpoint for creating restaurant
@app.route('/user_restaurants', methods=['POST'])
def create_restaurant():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid or expired token. Please quit and re-login'}), 401

    fields = request.get_json()
    if not fields['name'] or not fields['address']:
        return jsonify({'error': 'Required fields missing'}), 400
    
    if fields['is_public'] != True and fields['is_public'] != False:
        return jsonify({'error': '\"is_public\" field should be a boolean'}), 400
    
    try:
        fields['address'] = fields['address'].upper()
        fields['owner'] = user_id
        sql = 'INSERT INTO restaurants (name, address, chef_special, owner, tag, is_public) VALUES (%s, %s, %s, %s, %s, %s)'
        data = (fields['name'], fields['address'], fields['chef_special'], fields['owner'], fields['tag'], fields['is_public'])
        execute_query(sql, data)
        
        return jsonify({'message': 'restaurant entry created successfully'}), 200
    except:
        return jsonify({'error': 'Invalid field parameters'}), 400
    
# endpoint for updating user restaurants
@app.route('/user_restaurants', methods=['PUT'])
def update_restaurant():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid or expired token. Please quit and re-login'}), 401
    
    fields = request.get_json()
    if not fields['address']:
        return jsonify({'error': 'Address is required to update restaurant info'}), 400
    
    try:
        address = fields['address'].upper()
        del fields['address']
        sql = 'SELECT owner FROM restaurants WHERE address = %s'
        data = (address,)
        target = execute_query(sql, data)
        if not target:
            return jsonify({'error': 'No restaurant with this address'}), 404
        
        target_owner = target[0][0]
        if target_owner != user_id:
            return jsonify({'error': 'You have no access to modify this restaurant'}), 403
        
        field = list(fields.keys())[0]
        new_field = fields[field]
        if field == 'is_public':
            if new_field != True and new_field != False:
                return jsonify({'error': 'Invalid input for \'is_public\'. Has to be True or False'}), 400
            elif new_field == 'public':
                new_field = True
            else:
                new_field = False
        elif field == 'name' and not new_field:
            return jsonify({'error': 'New name cannot be empty'}), 400

        sql = 'UPDATE restaurants SET ' + field + ' = %s WHERE address = %s'
        data = (new_field, address)
        execute_query(sql, data)

        return jsonify({'message': 'restaurant entry modified successfully'}), 200
    except:
        return jsonify({'error': 'Invalid field parameters'}), 400
    
# endpoint for deleteing user restaurant
@app.route('/user_restaurants', methods=['DELETE'])
def delete_restaurant():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid or expired token. Please quit and re-login'}), 401
    
    address = request.get_json()
    if not address['address']:
        return jsonify({'error': 'Address is required to update restaurant info'}), 400
    address = address['address'].upper()
    
    sql = 'SELECT owner FROM restaurants WHERE address = %s'
    data = (address,)
    target = execute_query(sql, data)
    if not target:
        return jsonify({'error': 'No restaurant with this address'}), 404
    
    target_owner = target[0][0]
    if target_owner != user_id:
        return jsonify({'error': 'You have no access to delete this restaurant'}), 403
    
    try:
        sql = 'DELETE FROM restaurants WHERE address = %s'
        data = (address,)
        execute_query(sql, data)
        
        return jsonify({'message': 'Restaurant is successfully deleted'}), 204
    except:
        return jsonify({'error': 'failed to delete restaurant'}), 400

# endpoint for retrieving a 
@app.route('/random_number', methods=['GET'])
def random_number():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid or expired token. Please quit and re-login'}), 401

    try:
        response = requests.get('https://www.random.org/integers/?num=1&min=1&max=100&col=1&base=10&format=plain&rnd=new')

        return jsonify({'random number': response.text}), 200
    except:
        return jsonify({'error': 'failed to retrieve a random number'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)









