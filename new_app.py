from flask import Flask, render_template, request
# Import sqlalachemy
from sqlalchemy import create_engine,text
import os
import openai
from sqlalchemy import create_engine, text

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



# Load OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API")

# Load OpenAI prompt from text file
#with open("openai_prompt.txt") as f:
#    openai_prompt = f.read()

openai_prompt = """
Given the following database table schema:

Table Name: py_clinician_mips_2021
Variables:
- NPI: Unique clinician ID assigned by NPPES.
- Ind_PAC_ID: Unique individual clinician ID assigned by PECOS.
- lst_nm: Individual clinician last name.
- frst_nm: Individual clinician first name.
- APM_affl_1: Name of the Alternative Payment Model (APM) in which the individual eligible clinician participates (first affiliation).
- APM_affl_2: Name of the Alternative Payment Model (APM) in which the individual eligible clinician participates (second affiliation).
- APM_affl_3: Name of the Alternative Payment Model (APM) in which the individual eligible clinician participates (third affiliation).
- measure_cd: Components of measure code: [program][reporting_entity][measure_number]_[stratum], where program is defined as MIPS, QCDR, PI, or IA; reporting entity is indicated as EC for individual eligible clinician; measure number denotes the measure number or string identifier; and stratum indicates whether it is an overall rate or a single stratum.
- measure_title: Measure or attestation title.
- invs_msr: Indicator for whether a measure is an inverse measure.
- attestation_value: Attestation value.
- prf_rate: Measure performance rate (numeric).
- patient_count: Number of patients included in the measure denominator (numeric).
- star_value: Star rating, assigned based on performance at the measure, stratum, collection type, and entity type level (numeric).
- five_star_benchmark: The established ABC™ benchmark used to assign a five-star rating for a given measure and collection type (numeric).
- collection_type: Collection types are defined as ATT for Web Attestation, CLM for Claims, EHR for Electronic Health Record, QCDR for Qualified Clinical Data Registry, and REG for Qualified Registry. Note: Collection type is not published for PI and IA attestations.
- CCXP_ind: Indicator for whether the measure/attestation is reported on Care Compare profile pages (i.e., measures with an N value are only available in the PDC).

Convert this natural language query into SQL.: 
"""


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        if request.form['input_type'] == 'question':
            # Generate SQL from question using OpenAI's GPT-3 API
            #prompt = f"Convert this natural language query into SQL: {input_text}"
            prompt = openai_prompt + input_text + "\n\nPlease ensure to double-quote each field name in the SQL and limit the return to 100 rows.\nSQL:"
            model = "text-davinci-003"
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5,
            )
            sql = response.choices[0].text.strip()
        else:
            # Use SQL entered by the user
            sql = request.form['input_text']
        sql = sql.replace('\r', '').replace('\n', ' ')
        with engine.connect() as conn:
            results = conn.execute(text(sql)).fetchall()
        rows_dict = [row._asdict() for row in results]
        return render_template('new_index.html', results=rows_dict, input_text=input_text, sql=sql)
    else:
        return render_template('new_index.html')

if __name__ == '__main__':
    app.run(debug=True)
