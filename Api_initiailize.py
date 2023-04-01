import mysql.connector

# mySQL database configurations
config = {
    'user': 'root',
    'password': 'Password111!',
    'host': 'localhost',
    'database': 'HTTP_API'
}

cnx = mysql.connector.connect(**config)

# restaurant pre-fill list
restaurants = [
    {
        'name': 'restaurant1',
        'address': '1234 EXAMPLE ST',
        'chef_special': 'res1dish',
        'owner': '592f05f7-1d16-4bb6-9830-24b95f15d18b',
        'tag': 'wallet-friendly',
        'is_public': True
    },

    {
        'name': 'restaurant2',
        'address': '5678 EXAMPLE ST',
        'chef_special': 'res2dish',
        'owner': '592f05f7-1d16-4bb6-9830-24b95f15d18b',
        'tag': 'romantic',
        'is_public': True
    },

    {
        'name': 'restaurant3',
        'address': '1357 EXAMPLE ST',
        'chef_special': 'res3dish',
        'owner': '06f22dfa-9c7c-4aef-aac0-0246ea769c19',
        'tag': 'outdoor',
        'is_public': True
    }
]

# users pre-fill list
users = [
    {
        'id': '592f05f7-1d16-4bb6-9830-24b95f15d18b',
        'email': 'john@example.com',
        'password': 'ExamplePassword1!'
    },
    {
        'id': '06f22dfa-9c7c-4aef-aac0-0246ea769c19',
        'email': 'jane@example.com',
        'password': 'ExamplePassword2!'
    }
]

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
        cnx.commit()
        result = None

    cursor.close()
    return result

# pre-fill the mySQL database with public elements
for r in restaurants:
    sql = 'INSERT INTO restaurants (name, address, chef_special, owner, tag, is_public) VALUES (%s, %s, %s, %s, %s, %s)'
    data = (r['name'], r['address'], r['chef_special'], r['owner'], r['tag'], r['is_public'])
    execute_query(sql, data)

# users pre-fill list
users = [
    {
        'id': '592f05f7-1d16-4bb6-9830-24b95f15d18b',
        'email': 'john@example.com',
        'password': 'ExamplePassword1!'
    },
    {
        'id': '06f22dfa-9c7c-4aef-aac0-0246ea769c19',
        'email': 'jane@example.com',
        'password': 'ExamplePassword2!'
    }
]

for u in users:
    sql = 'INSERT INTO users (id, email, password) VALUES (%s, %s, %s)'
    data = (u['id'], u['email'], u['password'])
    execute_query(sql, data)

sql = 'SELECT * FROM users WHERE email = %s'
data = ('john@example.com',)
user_data = execute_query(sql, data)
print(user_data)









