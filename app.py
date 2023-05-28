from flask import Flask, render_template, request
# Import sqlalachemy
from sqlalchemy import create_engine,text
import os
import openai
import pandas as pd

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import load_tools
from langchain import SQLDatabase, SQLDatabaseChain


# Create an instance of Flask

app = Flask(__name__)

# import the dotenv library
from dotenv import load_dotenv
load_dotenv()
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

db_port = 5439
db_uri = f"redshift+psycopg2://{db_username}:{db_password}@{db_host}:5439/{db_name}"
engine = create_engine(db_uri)

# Load OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API")


llm = OpenAI(openai_api_key=os.environ.get("OPENAI_API"), temperature=0)
db = SQLDatabase.from_uri(db_uri)
db_chain = SQLDatabaseChain(llm=llm,database=db,verbose=True,use_query_checker=True, return_intermediate_steps=True)

# Get the absolute path to the "data" directory
data_dir = os.path.abspath("data")

# Use the absolute path when reading the CSV file
data_dict = pd.read_csv(os.path.join(data_dir, "data_dictionary.csv"),encoding='latin-1')
table_name_list = data_dict['Table Name'].unique().tolist()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        if request.form['input_type'] == 'question':
            # Generate SQL from question using OpenAI's GPT-3 API
            #prompt = f"Convert this natural language query into SQL: {input_text}"
            #prompt = openai_prompt + input_text + "\n\ Use limit clause return a maximum of 100 rows and write the SQL in the postgresql syntax. Write the SQL with the fully qualified column names so there is no ambiguity.\nPostgres SQL:"
            #model = "text-davinci-003"
            """
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                max_tokens=800,
                n=1,
                stop=None,
                temperature=0.2,
            )
            """
            #response = llm(prompt)
            #sql = response#.choices[0].text.strip()
            try:
                response = db_chain(input_text)
                ai_result = response['result']
                steps = response['intermediate_steps']
                string_steps = [i for i in steps if type(i)==str]
                return render_template('index.html', ai_result=ai_result, input_text=input_text,data = steps )
            except Exception as e:
                # Render the template with the SQL error
                return render_template('error.html', error=str(e))
        else:
            try:
                # Use SQL entered by the user
                sql = request.form['input_text']
                sql = sql.replace('\r', '').replace('\n', ' ')
                with engine.connect() as conn:
                    results = conn.execute(text(sql)).fetchall()
                rows_dict = [row._asdict() for row in results]
                return render_template('index.html', results=rows_dict, input_text=input_text, sql=sql)
            except Exception as e:
                # Render the template with the SQL error
                return render_template('error.html', error=str(e),query=sql)
    else:
        return render_template('index.html')
    

# Route to '/data_dict' that will render the data_dict.html template based on the data submitted from the form
"""
@app.route('/data_dict', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        table = request.form['table']
        # Filter the DataFrame based on the selected table
        filtered_data = data_dict[data_dict['Table Name'] == table]

        # Convert the filtered data to a list of dictionaries
        data = filtered_data.to_dict('records')

        return render_template('data_dict.html', data=data, table_names=table_name_list, selected_table=table)
    else:
        return render_template('data_dict.html',table_names=table_name_list,selected_table='')
    

@app.route('/questions', methods=['GET'])
def questions():
    return render_template('questions.html')
"""

if __name__ == '__main__':
    app.run(debug=True)
