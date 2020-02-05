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
sqlkey = Base.classes.geo_sentiment

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
    #json_string = df.to_json()
    #import json
    #json_string = json.dumps(df_dict)
    #print(json_string)
    
    transforming_columns = [df['Compound_Score'], df['Positive_Score'], df['Neutral_Score'], df['Negative_Score']]
    transformed_list = []
    for column in transforming_columns:
        thislist = column.to_list()
        newlist = []
        for item in thislist:
            item = item*100
            item = int(item)
            newlist.append(item)
        transformed_list.append(newlist)
    com_df = pd.DataFrame({"Compound_Score":transformed_list[0]})
    pos_df = pd.DataFrame({"Positive_Score":transformed_list[1]})
    neut_df = pd.DataFrame({"Neutral_Score":transformed_list[2]})
    neg_df = pd.DataFrame({"Negative_Score":transformed_list[3]})
    
    df = pd.DataFrame({"ID":df["ID"], 'User_Name':df['User_Name'], 'Tag':df['Tag'], 'Time_Stamp':df['Tag'],
                       'Text_of_Tweet':df['Text_of_Tweet'], "Compound_Score":com_df["Compound_Score"],
                       "Positive_Score":pos_df["Positive_Score"], "Neutral_Score":neut_df["Neutral_Score"],
                       "Negative_Score":neg_df["Negative_Score"], 'Location':df['Location'], 'Geocodes':df['Geocodes']})
    
    df_dict = df.to_dict()
    import json
    json_var = json.dumps(df_dict)
    return json_var
if __name__ == "__main__":
    app.run(debug=True)