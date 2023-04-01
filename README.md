Restaurant API

This API allows users to perform CRUD operations on a MySQL database of restaurant information, including restaurant name, address, chef's special, owner, and tag. Users can also register and log in to the API to access their own private restaurant information.

To immediately use the API, run the Api_use.py (API is currently running on AWS with public ip address 54.241.129.118 and port 5000, which is already configured in the file)

To configure and use the API locally, the following instructions will get you a copy of the project up and running on your local machine

Prerequisites:
Python 3.6 or higher
Flask
MySQL server

Installation:
1. pip install flask
2. pip install mysql.connector-python

Preparation (command-line and SQL):
mysql -u root -p(your password)
CREATE DATABASE HTTP_API;
USE HTTP_API;

Intialization files:
1. run the API_database_initialization.sql script to create the necessary tables for the API.
2. run the Api_initialize.py file to pre-fill the tables with 3 sample restaurants info and 2 dummy user accounts.
3. run the Api_code.py to start the flask app locally, but remember to change the 'password' field in the 'config' at the top of the file to your password.
4. run the Api_run.py to start using the API, but remember to change the url at the top of the file to http://localhost:5000/.

API Endpoints:
1. Register Endpoint:

    URL: /register

    Method: POST

    Request Body: json = {
        'email':
        'password':
    } 
    Password need to contain at least 10 characters, one lowercase letter, one uppercase letter and one of the following characters: !, @, #, ? or ]

    Response:
        - 201 Created: user registered successfully. Returns a JSON message with user id.
        - 400 Bad Request: Invalid email or password. Returns a JSON error message.

2. Login Endpoint:
    
    URL: /login

    Method: POST

    Request Body: json = {
        'email':
        'password':
    } 
    Password need to contain at least 10 characters, one lowercase letter, one uppercase letter and one of the following characters: !, @, #, ? or ]

    Response:
        - 200 OK: user logged in successfully. Returns a JSON message with a uuid4 token (required for subsequent protected endpoints).
        - 400 Bad Request: Invalid email or password. Returns a JSON error message.

For the following protected endpoints, a header with the login token is required.
    - header = {'Authorization': (your token)}.
    - The authentication token expires 20 minutes after login. After the token expires, it is crucial to logout first via the /logout endpoint before attempting logging in again.

3. Logout Endpoint:

    URL: /logout

    Method: DELETE

    Headers with token required

    Request Body: None

    Response:
        - 204 No Content: user logged out successfully. Active session is deleted from the MySQL table.

4. Public Restaurants Endpoint:

    URL: /public_restaurants

    METHOD: GET

    Headers with token required

    Request Body: params = {
        'page': (page number, default 1),
        'page_size': (number of restaurants per page, default 10)
    }

    Response:
        - 401 Unauthorized: token has expired. Returns a JSON message.
        - 200 OK: read request successful. Returns a list of JSON data on the public restaurants.
        - 400 Bad Request: Invalid parameters for pagination.

5. User Restaurants Endpoint:

    URL: /user_restaurants

    METHOD: GET

    Headers with token required

    Request Body: params = {
        'page': (page number, default 1),
        'page_size': (number of restaurants per page, default 10)
    }

    Response:
        - 401 Unauthorized: token has expired. Returns a JSON message.
        - 200 OK: read request successful. Returns a list of JSON data on the public restaurants.
        - 400 Bad Request: Invalid parameters for pagination. Returns a JSON message.

6. Create Restaurant Endpoint:

    URL: /user_restaurants

    METHOD: POST

    Headers with token required

    Request Body: json = {
                'name': (restaurant name),
                'address': (restaurant address),
                'chef_special': (chef's special dish),
                'tag': (restaurant tag),
                'is_public': (True or False)
            }

    Response:
        - 401 Unauthorized: token has expired. Returns a JSON message.
        - 200 OK: restaurant entry created successfully. Returns a JSON message.
        - 400 Bad Request: Invalid field parameters. Returns a JSON message.

7. Update Restaurant Endpoint:

    URL: /user_restaurants

    METHOD: PUT

    Headers with token required

    Request Body: json = {
                'address': (restaurant address),
                (field that need to be updated): (new value for the field)
            }
    Can only update one field at a time. Address, owner, and restaurant primary key cannot be updated.

    Response:
        - 401 Unauthorized: token has expired. Returns a JSON message.
        - 404 Not Found: no restaurant was found with the requested address. Returns a JSON message.
        - 403 Forbidden: no access to modify this restaurant (owner is not user). Returns a JSON message.
        - 200 OK: restaurant entry updated successfully. Returns a JSON message.
        - 400 Bad Request: Invalid field parameters. Returns a JSON message.

8. Delete Restaurant Endpoint:

    URL: /user_restaurants

    METHOD: DELETE

    Headers with token required

    Request Body: json = {'address': (restaurant address)}

    Response:
        - 401 Unauthorized: token has expired. Returns a JSON message.
        - 404 Not Found: no restaurant was found with the requested address. Returns a JSON message.
        - 403 Forbidden: no access to delete this restaurant (owner is not user). Returns a JSON message.
        - 204 No Content: restaurant is deleted successfully.
        - 400 Bad Request: failed to delete restaurant. Returns a JSON message.

9. Random Number Endpoint:

    URL: /random_number

    METHOD: GET

    Headers with token required

    Request Body: None

    Response:
        - 401 Unauthorized: token has expired. Returns a JSON message.
        - 200 OK: random number retrieved successfully. Returns a JSON message with the random number.
        - 400 Bad Request: failed to retrieve random number. Returns a JSON message.