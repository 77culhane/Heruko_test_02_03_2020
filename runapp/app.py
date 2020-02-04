import os

# Heroku check
is_heroku = False
if 'IS_HEROKU' in os.environ:
    is_heroku = True

# Flask
from flask import Flask, request, render_template

# SQL Alchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# PyMySQL
import pymysql

# Pandas
import pandas as pd

# Import your config
if is_heroku == False:
    from config import remote_db_endpoint, remote_db_port, remote_gwsis_dbname, remote_gwsis_dbuser, remote_gwsis_dbpwd
else:
    remote_db_endpoint = os.environ.get('remote_db_endpoint')
    remote_db_port = os.environ.get('remote_db_port')
    remote_gwsis_dbname = os.environ.get('remote_gwsis_dbname')
    remote_gwsis_dbuser = os.environ.get('remote_gwsis_dbuser')
    remote_gwsis_dbpwd = os.environ.get('remote_gwsis_dbpwd')
    
# Configure MySQL connection and connect 
pymysql.install_as_MySQLdb()
engine = create_engine(f"mysql://{remote_gwsis_dbuser}:{remote_gwsis_dbpwd}@{remote_db_endpoint}:{remote_db_port}/{remote_gwsis_dbname}")

# Set up SQL Alchemy connection and classes
Base = automap_base() # Declare a Base using `automap_base()`
Base.prepare(engine, reflect=True) # Use the Base class to reflect the database tables
sqlkey = Base.classes.geo_testing2

# Initialize Flask application
app = Flask(__name__)

#begin session
session = Session(engine)

@app.route("/")
def landing():
    return render_template("home.html")

@app.route("/home.html")
def home():
    return render_template("home.html")

@app.route("/maps.html")
def index():
    return render_template("maps.html")

@app.route("/bars.html")
def bars():
    return render_template("bars.html")


@app.route("/runquery")
def runquery():
    #query dataset
    results = session.query(sqlkey.ID, sqlkey.User_Name, sqlkey.Tag, sqlkey.Time_Stamp, sqlkey.Text_of_Tweet, sqlkey.Compound_Score, sqlkey.Positive_Score, sqlkey.Neutral_Score, sqlkey.Negative_Score, sqlkey.Location, sqlkey.Geocodes).all()
    
    df = pd.DataFrame(results, columns=['ID', 'User_Name', 'Tag', 'Time_Stamp', 'Text_of_Tweet', 'Compound_Score', 'Positive_Score', 'Neutral_Score', 'Negative_Score', 'Location', 'Geocodes'])
    #export to .csv
    df_dict = df.to_dict()
    import json
    json_string = json.dumps(df_dict)
    return json_string
if __name__ == "__main__":
    app.run(debug=True)