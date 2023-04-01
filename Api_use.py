import requests

# set up the API endpoint URLs
register_url = 'http://54.241.129.118:5000/register'
login_url = 'http://54.241.129.118:5000/login'
logout_url = 'http://54.241.129.118:5000/logout'
public_restaurants_url = 'http://54.241.129.118:5000/public_restaurants'
user_restaurants_url = 'http://54.241.129.118:5000/user_restaurants'
random_number_url = 'http://54.241.129.118:5000/random_number'

# set up the headers
headers = {}

# Login or Register
def Register():
    code = 0
    regemail = input('Enter email: ')
    regpwd = input('Enter password: ')
    data = {'email': regemail, 'password': regpwd}
    response = requests.post(register_url, json=data, headers=headers)
    code = response.status_code
    if code == 201:
        user = response.json()['user']
        print(f"User {user['id']} registered successfully.")
    else:
        print('Error code: ', code, ' ', response.text)

def Login():
    code = 0
    logemail = input('Enter email: ')
    logpwd = input('Enter password: ')
    data = {'email': logemail, 'password': logpwd}
    response = requests.post(login_url, json=data, headers=headers)
    code = response.status_code
    if code == 200:
        token = response.json()['token']
        print(f"Logged in successfully with token {token}.")
        return token
    else:
        print('Error code: ', code, ' ', response.text)
        token = ''
        return token

def LoginRegister():
    token = ''
    while not token:
        logreg = input('Login, Register, or Quit? (l/r/q) ')

        if logreg == 'r':
            # register a new user
            Register()
        elif logreg == 'l':
            # login with the registered user
            token = Login()
        elif logreg == 'q':
            token = 'quit'
        else:
            print('Invalid input, type \"l\" for login and \"r\" for register')
    
    return token

def read_public_restaurants(page, page_size):
    # read request for accessing restaurant info
    response = requests.get(public_restaurants_url, headers=headers, params={'page': page, 'page_size': page_size})
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print('Error:', response.status_code, ' ', response.text)

    return response.status_code

def read_user_restaurants(page, page_size):
    # read request for accessing restaurant info
    response = requests.get(user_restaurants_url, headers=headers, params={'page': page, 'page_size': page_size})
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print('Error:', response.status_code, ' ', response.text)

    return response.status_code

def create_restaurant(json):
    # post requests for creating a new user restaurant
    response = requests.post(user_restaurants_url, json=json, headers=headers)
    if response.status_code == 200:
        print(response.text)
    else:
        print('Error:', response.status_code, ' ', response.text)

    return response.status_code

def update_restaurant(json):
    # put requests for updating a user restaurant
    response = requests.put(user_restaurants_url, json=json, headers=headers)
    if response.status_code == 200:
        print(response.text)
    else:
        print('Error:', response.status_code, ' ', response.text)

    return response.status_code

def delete_restaurant(json):
    # delete requests for deleting a user restaurant
    response = requests.delete(user_restaurants_url, json=json, headers=headers)
    if response.status_code == 204:
        print('Restaurant deleted successfully')
    else:
        print('Error:', response.status_code, ' ', response.text)

    return response.status_code

def random_number():
    # retriving a random number from a public API
    response = requests.get(random_number_url, headers=headers)
    if response.status_code == 200:
        print(response.text)
    else:
        print('Error:', response.status_code, ' ', response.text)

    return response.status_code

def CRUD():
    action = ''
    code = 0
    while code != 401:
        action = input('Create, Read, Update, Delete, random number, or logout? (c/r/u/d/n/q) ') 
        if action == 'r':
            d = input('Public or User restaurants? (p/u): ')
            page = input('Page number (optional, default 1): ')
            page_size = input('Page size (optional, default 10): ')
            if not page:
                page = 1
            
            if not page_size:
                page_size = 10

            if d == 'p':
                code = read_public_restaurants(page, page_size)
            elif d == 'u':
                code = read_user_restaurants(page, page_size)
            else:
                print('Invalid input, type \"p\" for public restaurants and \"u\" for user-created restaurants')
        elif action == 'c':
            p = input('Public or private restaurants? (public/private) (required) ')
            if p == 'public':
                is_public = True
            elif p == 'private':
                is_public = False
            else:
                print('Invalid input, type either \"public\" or \"private\"')
                continue

            name = input('Restaurant name? (required) ')
            address = input('Restaurant address? (required) ')
            chef_special = input('What is the chef\'s special of your restaurant? (optional) ')
            tag = input('Any tag for your restaurant? (optional) ')
            json = {
                'name': name,
                'address': address,
                'chef_special': chef_special,
                'tag': tag,
                'is_public': is_public
            }
            code = create_restaurant(json)
        elif action == 'u':
            address = input('Address of the restaurant that needs to be updated? (required) ')
            field = input('What is the field that needs to be updated (name, special, tag, public)? (n/s/t/p) ')
            field_dict = {
                'n': 'name',
                's': 'chef_special',
                't': 'tag',
                'p': 'is_public'
            }
            if field not in field_dict:
                print('Invalid input, type \"n\" for restaurant name, \"s\" for chef\'s special, \"t\" for tag, and \"p\" for public or private.')
                continue

            new_field = input(f'New {field_dict[field]}? ')

            json = {
                'address': address,
                field_dict[field]: new_field
            }
            code = update_restaurant(json)
        elif action == 'd':
            address = input('Address of the restaurant that needs to be deleted? (required) ')
            json = {'address': address}
            code = delete_restaurant(json)
        elif action == 'n':
            code = random_number()
        elif action == 'q':
            break
        else:
            print('Invalid input, type \"c\" for create, \"r\" for read, \"u\" for update, \"d\" for delete, and \"q\" for quitting the current session.')
        
    response = requests.delete(logout_url, headers=headers)
    if code == 401:
        print('Session expired. Please re-login')
    elif response.status_code == 204:
        print("Logged out successfully.")
    else:
        print('Error:', response.status_code, ' ', response.text)

if __name__ == '__main__':
    token = 'something'
    while token:
        token = LoginRegister()
        if token == 'quit':
            break
        headers['Authorization'] = token
        CRUD()

    
    









