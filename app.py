import json

from flask import Flask,render_template, request, redirect, url_for , jsonify, Response
from flask_mysqldb import MySQL
from datetime import datetime
import csv
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

## Required MYSQL - Login Details
# app.config["MYSQL_USER"] = "root"
# app.config["MYSQL_PASSWORD"] = "password"
# app.config["MYSQL_DB"] = "classicmodels"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@0.0.0.0:3036/classicmodels'
# db = SQLAlchemy(app)


app.config['MYSQL_HOST'] = '0.0.0.0'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'classicmodels'

mysql = MySQL(app)

## 1. Setting up MySQL connection cursor
# cursor = mysql.connection.cursor()
## 2. Executing SQL Statements
# cursor.execute(''' CREATE TABLE table_name(field1, field2...) ''')
## 3. Saving the Actions performed on the DB
# mysql.connection.commit()
## 4. Closing the cursor
# cursor.close()

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/createTables')
def createTables():
    cursor = mysql.connection.cursor()
    cursor.execute('''CREATE TABLE classicmodels.TableLogins(
        username varchar(255),
        password varchar(255))
    ''')
    cursor.execute('''CREATE TABLE classicmodels.TablePersons(
        PersonID int,
        LastName varchar(255),
        FirstName varchar(255),
        Address varchar(255),
        City varchar(255)
    )''')
    mysql.connection.commit()
    cursor.close()
    return f"Done!!"


# Function to get products from the database
def get_products():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM classicmodels.products")
    products = cursor.fetchall()
    cursor.close()
    return products

@app.route('/products')
def display_products():
    products = get_products()
    return render_template('products.html', products=products)

# it will do a GET request first.
# Only once you submit the form your browser will do a POST.
# So for a self-submitting form like yours, you need to handle both.
@app.route('/form', methods = ['POST', 'GET'])
def form():
    if request.method == 'POST':
        return 'POST'
    return render_template('form-register.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'GET':
        return "Login via the login Form"

    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        age = request.form['age']
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO classicmodels.TableLogins VALUES(%s,%s)''',(name,password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('index'))

@app.route('/loginform', methods = ['POST', 'GET'])
def loginform():
    if request.method == 'POST':
        return 'POST'
    return render_template('form-login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute('''SELECT password FROM classicmodels.TableLogins WHERE username = %s AND password = % s''', (username, password, ))
        account = cursor.fetchone()
        cursor.close()
        if account:
            print('Logged in successfully !')
            return redirect(url_for('display_products'))
        else:
            msg = 'Incorrect username / password !'
            return render_template('index.html', msg=msg)


@app.route('/upload', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        if 'csv_file' in request.files:
            csv_file = request.files['csv_file']

            if csv_file.filename != '':
                # Check if the file is ending with .csv
                if csv_file.filename.endswith('.csv'):
                    # Read and insert data from the CSV file
                    cursor = mysql.connection.cursor()

                    # Create the Product table with more columns
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS TableProducts (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            product_id VARCHAR(255),
                            name VARCHAR(255),
                            price DECIMAL(10, 2),
                            category VARCHAR(255),
                            manufacturer VARCHAR(255),
                            stock_quantity INT
                        );
                    ''')

                    # Read and insert data from the CSV file
                    csv_data = csv.reader(csv_file.stream.read().decode('utf-8').splitlines())
                    for row in csv_data:
                        cursor.execute('''INSERT INTO TableProducts(product_id, name, price, category, manufacturer, stock_quantity) 
                                          VALUES (%s, %s, %s, %s, %s, %s)''',
                                       (row[0], row[1], float(row[2]), row[3], row[4], int(row[5])))

                    mysql.connection.commit()
                    cursor.close()

                    return redirect(url_for('display_products'))

    return render_template('upload.html')


@app.route('/analyze/category', methods=['GET'])
def analyze_products_by_category():
    conn = mysql.connection # Change to your database
    cursor = conn.cursor()

    # Execute an SQL query to count products by category
    cursor.execute("SELECT category, COUNT(*) FROM TableProducts GROUP BY category")
    results = cursor.fetchall()
    cursor.close()
    print(f"results - {results}")

    if results:
        # Create the histogram
        categories = []
        counts = []
        for row in results:
            category = row[0]
            count = row[1]
            categories.append(category)
            counts.append(count)

        # Plot the histogram
        plt.figure()
        plt.bar(categories, counts)
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.title("Number of Products by Category")

        # Save the plot to a file
        plt.savefig("static/histogram.png")

        return render_template('analysis-product.html')
    else:
        response = {"error": "No products found for category analysis."}
        return jsonify(response), 404



@app.route('/statisticalanalysis', methods=['GET'])
def statisticalanalysis_products():
    conn = mysql.connection # Change to your database
    cursor = conn.cursor()

    # Analysis 1: Total Stock Quantity
    cursor.execute("SELECT SUM(stock_quantity) FROM TableProducts")
    total_stock_quantity = cursor.fetchone()[0]

    # Analysis 2: Average Price by Category
    cursor.execute("SELECT category, AVG(price) FROM TableProducts GROUP BY category")
    average_prices_by_category = cursor.fetchall()

    # Analysis 3: Most Expensive and Least Expensive Products
    cursor.execute("SELECT name, price FROM TableProducts WHERE price = (SELECT MAX(price) FROM TableProducts)")
    most_expensive_product = cursor.fetchone()
    cursor.execute("SELECT name, price FROM TableProducts WHERE price = (SELECT MIN(price) FROM TableProducts)")
    least_expensive_product = cursor.fetchone()

    # Analysis 4: Count of Products per Manufacturer
    cursor.execute("SELECT manufacturer, COUNT(*) FROM TableProducts GROUP BY manufacturer")
    products_per_manufacturer = cursor.fetchall()

    # Analysis 5: Price Range Analysis
    cursor.execute("SELECT MIN(price), MAX(price) FROM TableProducts")
    price_range_data = cursor.fetchone()

    # Close the database connection
    cursor.close()

    return render_template('analysis.html',
                           total_stock_quantity=total_stock_quantity,
                           average_prices_by_category=average_prices_by_category,
                           most_expensive_product=most_expensive_product,
                           least_expensive_product=least_expensive_product,
                           products_per_manufacturer=products_per_manufacturer,
                           price_range_data=price_range_data)



if __name__ == '__main__':
    app.run()
