"""
Write a flask application that connects to a database and allows users to query the database displaying the results in a table on the webpage.
The application should have a homepage that displays a form that allows users to enter a SQL query.
The application should have a results page that displays the results of the query in a table.
"""
from flask import Flask, render_template, request
# Import sqlalachemy
from sqlalchemy import create_engine,text
import os

# Create an instance of Flask

app = Flask(__name__)

# import the dotenv library
from dotenv import load_dotenv

# Configure the database connection to an AWS RDS instance
# The connection string format is:
# dialect://username:password@host:port/database

# Load username from environment variable
db_username = os.environ.get('DB_USERNAME')
# Load password from environment variable
db_password = os.environ.get('DB_PASSWORD')
# Load host from environment variable
db_host = os.environ.get('DB_HOST')
# Load database name from environment variable
db_name = os.environ.get('DB_NAME')

db_port = 5432
engine = create_engine(f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:5432/{db_name}")

# Create a route decorator
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sql = request.form['sql'].replace('\r', '').replace('\n', ' ')
        with engine.connect() as conn:
            results = conn.execute(text(sql)).fetchall()
        return render_template('index.html', results=results, sql=sql)
    else:
        return render_template('index.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True) # Set debug to false for production apps
