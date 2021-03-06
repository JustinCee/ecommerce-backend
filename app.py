import hmac
import sqlite3
import datetime
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS


# This function create dictionaries out of SQL rows, so that the data follows JSON format
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# Function to create USER table
def init_user_table():
    conn = sqlite3.connect('pos.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "full_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# Function to create PRODUCT table
def init_product_table():
    with sqlite3.connect('pos.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS products(prod_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "user_id INTEGER NOT NULL,"
                     "title TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "FOREIGN KEY (user_id) REFERENCES user (user_id))")
    print("blog table created successfully.")


init_user_table()
init_product_table()

# API setup
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'


# ROUTES
@app.route('/', methods=["GET"])
def welcome():
    response = {}
    if request.method == "GET":
        response["message"] = "Welcome"
        response["status_code"] = 201
        return response


@app.route('/user/', methods=["POST", "GET", "PATCH"])
def user_registration():
    response = {}

    # Fetches ALL users
    if request.method == "GET":
        with sqlite3.connect("pos.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user")
            users = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = users
        return response

    # LOGIN
    if request.method == "PATCH":
        email = request.json["email"]
        password = request.json["password"]

        with sqlite3.connect("pos.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password,))
            user = cursor.fetchone()

        response['status_code'] = 200
        response['data'] = user
        return response

    # REGISTER
    if request.method == "POST":
        try:
            full_name = request.json['full_name']
            email = request.json['email']
            password = request.json['password']

            with sqlite3.connect("pos.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user("
                               "full_name,"
                               "email,"
                               "password) VALUES(?, ?, ?)", (full_name, email, password))
                conn.commit()
                response["message"] = "successfully added new user to database"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed"
            response["status_code"] = 209
            return response


@app.route('/user/<int:user_id>', methods=["GET"])
def get_user(user_id):
    response = {}
    with sqlite3.connect("pos.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id=" + str(user_id))

        user = cursor.fetchone()

    response['status_code'] = 200
    response['data'] = user
    return response


@app.route('/product/', methods=["POST", "GET"])
def products():
    response = {}

    # GET ALL PRODUCTS
    if request.method == "GET":
        with sqlite3.connect("pos.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            users = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = users
        return response

    # Create a new product
    if request.method == "POST":
        try:
            user_id = request.json['user_id']
            title = request.json['title']
            description = request.json['description']
            image = request.json['image']
            price = request.json['price']

            with sqlite3.connect("pos.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products("
                               "user_id, "
                               "title, "
                               "description, "
                               "image, "
                               "price) VALUES(?, ?, ?, ?, ?)", (user_id, title, description, image, price))
                conn.commit()
                response["message"] = "successfully added new product to database"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to create product"
            response["status_code"] = 209
            return response


@app.route('/product/<int:user_id>', methods=["GET"])
def get_user_products(user_id):
    response = {}

    # GET ALL PRODUCTS
    if request.method == "GET":
        with sqlite3.connect("pos.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE user_id=" + str(user_id))
            user_products = cursor.fetchall()

        response['status_code'] = 200
        response['data'] = user_products
        return response


@app.route('/edit-product/<int:product_id>', methods=["PUT"])
def change_user_product(product_id):
    response = {}

    if request.method == "PUT":
        try:
            user_id = request.json['user_id']
            title = request.json['title']
            description = request.json['description']
            image = request.json['image']
            price = request.json['price']

            with sqlite3.connect("pos.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE product SET title=? AND description=? AND image=? AND price=? WHERE user_id=? "
                               "AND prod_id=?", (title, description, image, price, user_id, product_id))
                conn.commit()
                response["message"] = "Product was successfully updated"
                response["status_code"] = 201
            return response
        except ValueError:
            response["message"] = "Failed to update product"
            response["status_code"] = 209
            return response


if __name__ == '__main__':
    app.run(debug=True)
