from flask import Flask, render_template, request
# Import sqlalachemy
from sqlalchemy import create_engine,text
import os
import openai
import pandas as pd

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import load_tools,create_sql_agent
from langchain import SQLDatabase, SQLDatabaseChain
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType


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

llm = OpenAI(openai_api_key=os.environ.get("OPENAI_API"), temperature=0,max_tokens=800)
db = SQLDatabase.from_uri(db_uri)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    return_intermediate_steps=True,
)


# Get the absolute path to the "data" directory
data_dir = os.path.abspath("data")

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        if request.form['input_type'] == 'question':
            # Generate SQL from question using OpenAI's GPT-3 API
            try:
                response = agent_executor(input_text)
                ai_result = response['output']
                #steps = response['intermediate_steps']
                #string_steps = [i for i in steps if type(i)==str]
                return render_template('index.html', ai_result=ai_result, input_text=input_text)
            except Exception as e:
                # Render the template with the SQL error
                print(input_text)
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
    

if __name__ == '__main__':
    app.run(debug=True)
