from flask import Flask, render_template, request
# Import sqlalachemy
from sqlalchemy import create_engine,text
import os
import openai
from sqlalchemy import create_engine, text
import pandas as pd

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

db_port = 5432
engine = create_engine(f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:5432/{db_name}")



# Load OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API")

# Load OpenAI prompt from text file
#with open("openai_prompt.txt") as f:
#    openai_prompt = f.read()

openai_prompt = """
Given the following postgres database table schema:

Table Name: py_clinician_mips_2021
Variable Name: npi
Description: Unique clinician ID assigned by NPPES.

Variable Name: ind_pac_id
Description: Unique individual clinician ID assigned by PECOS.

Variable Name: lst_nm
Description: Individual clinician last name.

Variable Name: frst_nm
Description: Individual clinician first name.

Variable Name: mid_nm
Description: Individual clinician middle name.

Variable Name: suff
Description: Individual clinician suffix.

Variable Name: facility_type
Description: Facilities can fall into the following type categories.

Variable Name: facility_afl_ccn
Description: Medicare CCN of facility type or unit within hospital where an individual clinician provides service.

Variable Name: parent_ccn
Description: The Medicare CCN of the primary hospital where individual clinician provides service.

Table Name: chronic_condition_puf
Variable Name: Bene_Geo_Lvl
Description: Identifies the level of geography that the data in the row has been aggregated. A value of 'County' indicates the data in the row is aggregated to the county level and identifies a Medicare beneficiary's geographic place of residence. A value of 'State' indicates the data in the row is aggregated to a single state identified as a Medicare beneficiary's geographic place of residence. 

Variable Name: Bene_Geo_Desc
Description: Identifies the demographic level of the population that the data has been aggregated. A value of 'All' indicates the data in the row represents all Fee-for-Service Medicare beneficiaries. A value of 'Sex' indicates that the data has been aggregated by the Medicare beneficiary's sex. A value of 'Race' indicates that the data has been aggregated by the Medicare beneficiary's race. 

Variable Name: Bene_Geo_Cd
Description: Identifies the demographic level of the population that the data has been aggregated. A value of 'All' indicates the data in the row represents all Fee-for-Service Medicare beneficiaries. A value of 'Sex' indicates that the data has been aggregated by the Medicare beneficiary's sex. A value of 'Race' indicates that the data has been aggregated by the Medicare beneficiary's race.

Variable Name: Bene_Age_Lvl
Description: Identifies the demographic level of the population that the data has been aggregated. A value of 'All' indicates the data in the row represents all Fee-for-Service Medicare beneficiaries. A value of 'Sex' indicates that the data has been aggregated by the Medicare beneficiary's sex. A value of 'Race' indicates that the data has been aggregated by the Medicare beneficiary's race. 

Variable Name: Bene_Demo_Desc
Description: For Bene_Demo_Lvl='Sex', a beneficiary's sex is classified as Male or Female and is identified using information from the CMS enrollment database. For Bene_Demo_Lvl='Race', the race/ethnicity classifications are: Non-Hispanic White, Black or African American, Asian/Pacific Islander, Hispanic, and American Indian/Alaska Native. 

Variable Name: Bene_MCC
Description: To classify MCC for each Medicare beneficiary, the 21 chronic conditions are counted and grouped into four categories (0-1, 2-3, 4-5 and 6 or more).

Variable Name: Prvlnc
Description: Prevalence estimates are calculated by taking the beneficiaries within MCC category divided by the total number of beneficiaries in our fee-for-service population, expressed as a percentage.

Variable Name: Tot_Mdcr_Stdzd_Pymt_PC
Description: Medicare standardized spending includes total Medicare payments for all covered services in Parts A and B and is presented per beneficiary (i.e., per capita). Standardized payments are presented to allow for comparisons across geographic areas in healthcare use among beneficiaries.

Variable Name: Tot_Mdcr_Pymt_PC
Description: Medicare spending includes total Medicare payments for all covered services in Parts A and B and is presented per beneficiary (i.e., per capita).

Variable Name: Hosp_Readmsn_Rate
Description: Hospital readmissions are expressed as a percentage of all admissions. A 30-day readmission is defined as an admission to an acute care hospital for any cause within 30 days of discharge from an acute care hospital. 

Variable Name: ER_Visits_Per_1000_Benes
Description: Emergency department visits are presented as the number of visits per 1,000 beneficiaries.

Table Name: puf_quality_payment_program

Variable Name: Provider_Key
Description: Random unique key assigned to each row.

Variable Name: Practice_State_or_US_territory
Description: The State or United States (US) territory code location of the TIN associated with the clinician.

Variable Name: Practice_Size
Description: Count of clinicians associated with TIN from the second segment of the MIPS eligibility determination period.

Variable Name: Clinician_Specialty
Description: The specialty description is an identifier corresponding to the type of service that the clinician submitted most on their Medicare Part B claims for this TIN/NPI combination.

Variable Name: Years_in_Medicare
Description: The number of years since the first date an enrollment was approved for this NPI across all enrollments in PECOS.

Variable Name: NPI
Description: The National Provider Identifier assigned to the clinician when they enrolled in Medicare. Multiple rows for the same NPI indicate multiple TIN/NPI combinations.

Variable Name: Engaged
Description: Indicates if the clinician reported a minimum of one measure or activity as an individual or group, or participated in a MIPS APM.

Variable Name: Participation_Type
Description: Indicates the level at which performance data was collected, submitted, or reported for the final score attributed to the clinician. All data elements from this point forward are based on the Participation Type identified in the preceding column (column 8).

Variable Name: Medicare_Patients
Description: The number of Medicare patients who received covered professional services during one segment of the MIPS eligibility determination period that was attributed to the participation type associated with the clinician's final score.

Variable Name: Allowed_Charges
Description: The allowed charges under the Physician Fee Schedule on Medicare Part B claims with a service date during one segment of the MIPS eligibility determination period that was attributed to the participation type associated with the clinician's final score.

Variable Name: Services
Description: The number of covered professional services provided to Medicare Part B patients with a service date during one segment of the MIPS eligibility determination period that was attributed to the participation type associated with the clinician's final score.

Variable Name: Opted_Into_MIPS
Description: Indicates if an "opt-in eligible" clinician, group, or APM Entity elected to participate in MIPS and receive a payment adjustment. This status is attributed to the participation type associated with the clinician's final score.

Variable Name: Small_Practitioner
Description: Indicates if the clinician, group, or APM Entity had the small practice special (15 or fewer clinicians billed under the TIN or APM Entity) based on either segment of the MIPS eligibility determination period. Note: This number can contradict the practice size in column 3, which is always based on the 2nd segment.

Variable Name: Rural_Clinician
Description: Indicates if the clinician or group had the rural special status (practiced in a ZIP code designated as rural by the Federal Office of Rural Health Policy (FORHP) using the most recent FORHP Eligible ZIP code file available).

Variable Name: HPSA_Clinician
Description: Indicates if the clinician or group had the HPSA special status (practiced in a Health Professional Shortage Area (HPSA)).

Variable Name: Ambulatory_Surgical_Center
Description: Indicates if the clinician or group had the ambulatory surgical center-based special status (determined by the volume of their covered professional services furnished in an ambulatory surgical center). This status is attributed to the participation type associated with the clinician's final score.

Variable Name: HospitalBased_Clinician
Description: Indicates if the clinician or group had the hospital-based special status (determined by the volume of their covered professional services furnished in a hospital setting). This status is attributed to the participation type associated with the clinician's final score.

Variable Name: Non-Patient_Facing
Description: Indicates if the clinician or group has the facility-based special status (based on the volume of services furnished in a facility eligible for the Hospital Value-based Purchasing program). This status is attributed to the participation type associated with the clinician's final score.

Variable Name: FacilityBased
Description: Indicates if the clinician or group has the facility-based special status (based on the volume of services furnished in a facility eligible for the Hospital Value-based Purchasing program). This status is attributed to the participation type associated with the clinician's final score.

Variable Name: Extreme_Hardship
Description: Indicates if the clinician or group was affected by an extreme and uncontrollable circumstance (EUC) (such as FEMA-designated major disaster) and qualified for performance category reweighting because of the MIPS automatic EUC policy or MIPS EUC exception application. This indicator is attributed to the participation type associated with the clinician's final score.

Variable Name: Final_Score
Description: The MIPS final score attributed to the clinician (the highest final score that could be attributed to the clinician's TIN/NPI combination). This is based on the participation type associated with the clinician's final score.

Variable Name: Payment_Adjustment
Description: The total payment adjustment attributed to the clinician for the 2022 payment year. Payment adjustments are determined by comparing the final score to the performance thresholds and then scaled to ensure budget neutrality.

Variable Name: Complex_Patient_Bonus
Description: The complex patient bonus associated with the final score attributed to the clinician.

Variable Name: Extreme_Hardship_Quality
Description: Indicates if the clinician, group, or APM Entity was approved for reweighting of the quality performance category due to extreme and uncontrollable circumstances. This indicator is attributed to the participation type associated with the clinician's final score.

Variable Name: Quality_Category_Score
Description: This is the unweighted score received for the quality score that is used for the overall score.

Variable Name: Quality_Bonus
Description: The bonus points received for the quality category (small practice bonus and quality improvement, if applicable).

Variable Name: Quality_Measure_ID_X
Description: MIPS Quality ID for one of the quality measures that contributed to the final score.

Variable Name: Quality_Measure_Score_X
Description: Measure score (including bonus points) achieved for the corresponding MIPS Quality ID that contributed to the final score.

Variable Name: Promoting_Interoperability_(PI)_Category_score
Description: This is the unweighted score received by the participant for the Promoting Interoperability category that is used for the overall score.

Variable Name: Extreme_Hardship_PI
Description: Indicates if the clinician, group, or APM Entity was approved for reweighting of the Promoting Interoperability performance category due to extreme and uncontrollable circumstances.

Variable Name: PI_Hardship
Description: Indicates if the clinician or group was approved for an exception from the Promoting Interoperability performance category due to participation in a small practice, decertified Electronic Health Record (EHR) technology, insufficient Internet connectivity, or lack of control over the availability of certified EHR technology (CEHRT).

Variable Name: PI_Reweighting
Description: Indicates if the clinician or group qualified for an automatic reweighting from the Promoting Interoperability performance category due to special status or clinician specialty.

Variable Name: PI_Bonus_
Description: The total bonus points received by the clinician, group, or APM Entity for the Promoting Interoperability performance category.

Variable Name: PI_CEHRT_ID_(measurem_ent_set__cehrt_id)
Description: This is a unique identifier generated by the Office of the National Coordinator for Health Information Technology (ONC) and identifies a specific bundle of software or EHR. The CEHRT ID is a 15-character alphanumeric string which can be found on the CHPL website. This is the CEHRT ID included in the data that contributed to the clinician's final score.

Variable Name: PI_Measure_ID_X
Description: MIPS Promoting Interoperability ID for one of the Promoting Interoperability measures that contributed to the final score.

Variable Name: PI_Measure_Score_X
Description: Measure score achieved for the corresponding MIPS Promoting Interoperability ID that contributed to the final score.

Variable Name: IA_Score
Description: The score received for the improvement activities performance category based on all the activities picked for the category that contributed to the final score.

Variable Name: Extreme_Hardship_IA
Description: Indicates if the clinician, group, or APM Entity was approved for reweighting of the improvement activities performance category due to extreme and uncontrollable circumstances.

Variable Name: IA_Study
Description: This data element will show as FALSE for everyone because this study concluded after the 2019 performance year.

Variable Name: IA_Measure_ID_X
Description: MIPS Improvement Activity ID for one of the improvement activities that contributed to the final score.

Variable Name: IA_Measure_Score_X
Description: Activity score achieved for the corresponding MIPS Improvement Activity ID that contributed to the final score.

Variable Name: Cost_Score
Description: The unweighted score received for the cost performance category based on all the cost measures used for final scoring. Will display as '0' for all clinicians because cost was reweighted in the 2020 performance year.

Variable Name: Extreme_Hardship_Cost
Description: Indicates if the clinician was approved for reweighting of the cost performance category due to extreme and uncontrollable circumstances.
reweighted for all individuals and groups.)

Variable Name: Cost_Measure_ID_X
Description: MIPS Cost ID for one of the cost measures that contributed to the final score.

Variable Name: Cost_Measure_Score_X
Description: Cost score achieved for the corresponding MIPS Cost ID that contributed to the final score.

Convert this natural language query into SQL based on the tables defined above in the database: 
"""

# Get the absolute path to the "data" directory
data_dir = os.path.abspath("data")

# Use the absolute path when reading the CSV file
data_dict = pd.read_csv(os.path.join(data_dir, "data_dictionary.csv"),encoding='latin-1')
table_name_list = data_dict['Table Name'].unique().tolist()

app = Flask(__name__)
print(f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:5432/{db_name}")

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            input_text = request.form['input_text']
            if request.form['input_type'] == 'question':
                # Generate SQL from question using OpenAI's GPT-3 API
                #prompt = f"Convert this natural language query into SQL: {input_text}"
                prompt = openai_prompt + input_text + "\n\ Use limit clause to only return a maximum of 100 rows and write the SQL in the postgresql syntax.\nSQL:"
                model = "text-davinci-003"
                response = openai.Completion.create(
                    engine=model,
                    prompt=prompt,
                    max_tokens=824,
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
            return render_template('index.html', results=rows_dict, input_text=input_text, sql=sql)
        else:
            return render_template('index.html')
    except Exception as e:
        # Render the template with the SQL error
        return render_template('error.html', error=str(e),query=sql)

# Route to '/data_dict' that will render the data_dict.html template based on the data submitted from the form
@app.route('/data_dict', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        table = request.form['table']
        # Filter the DataFrame based on the selected table
        filtered_data = data_dict[data_dict['Table Name'] == table]

        # Convert the filtered data to a list of dictionaries
        data = filtered_data.to_dict('records')

        return render_template('data_dict.html', data=data, table_names=table_name_list)
    else:
        return render_template('data_dict.html',table_names=table_name_list)
    
@app.route('/questions', methods=['GET'])
def questions():
    return render_template('questions.html')

if __name__ == '__main__':
    app.run(debug=True)
