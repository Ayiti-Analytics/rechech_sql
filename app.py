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
Variable Label: NPI
Description: Unique clinician ID assigned by NPPES.

Variable Name: ind_pac_id
Variable Label: PAC ID
Description: Unique individual clinician ID assigned by PECOS.

Variable Name: lst_nm
Variable Label: Last Name
Description: Individual clinician last name.

Variable Name: frst_nm
Variable Label: First Name
Description: Individual clinician first name.

Variable Name: mid_nm
Variable Label: Middle Name
Description: Individual clinician middle name.

Variable Name: suff
Variable Label: Suffix
Description: Individual clinician suffix.

Variable Name: facility_type
Variable Label: Facility Type
Description: Facilities can fall into the following type categories.

Variable Name: facility_afl_ccn
Variable Label: Facility Affiliations CCN
Description: Medicare CCN of facility type or unit within hospital where an individual clinician provides service.

Variable Name: parent_ccn
Variable Label: Facility Affiliations Parent CCN
Description: The Medicare CCN of the primary hospital where individual clinician provides service.

--------------------------------
Table Name: chronic_condition_puf
Variable Name: Bene_Geo_Lvl
Variable Label: Beneficiary Geographic Level
Description: Identifies the level of geography that the data in the row has been aggregated. A value of 'County' indicates the data in the row is aggregated to the county level and identifies a Medicare beneficiary's geographic place of residence. A value of 'State' indicates the data in the row is aggregated to a single state identified as a Medicare beneficiary's geographic place of residence. A value of 'National' indicates the data in the row is aggregated across all states, the District of Columbia, Puerto Rico, and the U.S. Virgin Islands.

Variable Name: Bene_Geo_Desc
Variable Label: Beneficiary Geographic Description
Description: Identifies the demographic level of the population that the data has been aggregated. A value of 'All' indicates the data in the row represents all Fee-for-Service Medicare beneficiaries. A value of 'Sex' indicates that the data has been aggregated by the Medicare beneficiary's sex. A value of 'Race' indicates that the data has been aggregated by the Medicare beneficiary's race. A value of 'Dual Status' indicates that the data has been aggregated by the Medicare beneficiary's dual eligibility status.

Variable Name: Bene_Geo_Cd
Variable Label: Beneficiary Geographic Code
Description: Identifies the demographic level of the population that the data has been aggregated. A value of 'All' indicates the data in the row represents all Fee-for-Service Medicare beneficiaries. A value of 'Sex' indicates that the data has been aggregated by the Medicare beneficiary's sex. A value of 'Race' indicates that the data has been aggregated by the Medicare beneficiary's race. A value of 'Dual Status' indicates that the data has been aggregated by the Medicare beneficiary's dual eligibility status.

Variable Name: Bene_Age_Lvl
Variable Label: Beneficiary Age Level
Description: Identifies the demographic level of the population that the data has been aggregated. A value of 'All' indicates the data in the row represents all Fee-for-Service Medicare beneficiaries. A value of 'Sex' indicates that the data has been aggregated by the Medicare beneficiary's sex. A value of 'Race' indicates that the data has been aggregated by the Medicare beneficiary's race. A value of 'Dual Status' indicates that the data has been aggregated by the Medicare beneficiary's dual eligibility status.

Variable Name: Bene_Demo_Desc
Variable Label: Beneficiary Demographic Description
Description: For Bene_Demo_Lvl='Sex', a beneficiary's sex is classified as Male or Female and is identified using information from the CMS enrollment database. For Bene_Demo_Lvl='Race', the race/ethnicity classifications are: Non-Hispanic White, Black or African American, Asian/Pacific Islander, Hispanic, and American Indian/Alaska Native. All the chronic condition reports use the variable RTI_RACE_CD, which is available on the Master Beneficiary Files in the CCW. For Bene_Demo_Lvl='Dual Status', beneficiaries can be classified as 'Medicare & Medicaid' or 'Medicare Only'. Beneficiaries enrolled in both Medicare and Medicaid are known as "dual eligibles." Medicare beneficiaries are classified as dual eligibles if in any month in the given calendar year they were receiving full or partial Medicaid benefits.

Variable Name: Bene_MCC
Variable Label: Beneficiary Multiple Chronic Condition Group
Description: To classify MCC for each Medicare beneficiary, the 21 chronic conditions are counted and grouped into four categories (0-1, 2-3, 4-5 and 6 or more).

Variable Name: Prvlnc
Variable Label: Prevalence
Description: Prevalence estimates are calculated by taking the beneficiaries within MCC category divided by the total number of beneficiaries in our fee-for-service population, expressed as a percentage.

Variable Name: Tot_Mdcr_Stdzd_Pymt_PC
Variable Label: Total Medicare Standardized Per Capita Spending
Description: Medicare standardized spending includes total Medicare payments for all covered services in Parts A and B and is presented per beneficiary (i.e., per capita). Standardized payments are presented to allow for comparisons across geographic areas in healthcare use among beneficiaries. More information on the standardization of Medicare payments can be found here.

Variable Name: Tot_Mdcr_Pymt_PC
Variable Label: Total Medicare Per Capita Spending
Description: Medicare spending includes total Medicare payments for all covered services in Parts A and B and is presented per beneficiary (i.e., per capita).

Variable Name: Hosp_Readmsn_Rate
Variable Label: Hospital Readmission Rate
Description: Hospital readmissions are expressed as a percentage of all admissions. A 30-day readmission is defined as an admission to an acute care hospital for any cause within 30 days of discharge from an acute care hospital. Except when the patient died during the stay, each inpatient stay is classified as an index admission, a readmission, or both.

Variable Name: ER_Visits_Per_1000_Benes
Variable Label: Emergency Room Visits per 1,000 Beneficiaries
Description: Emergency department visits are presented as the number of visits per 1,000 beneficiaries. ED visits include visits where the beneficiary was released from the outpatient setting and where the beneficiary was admitted to an inpatient setting.

--------------------------------
Table Name: puf_quality_payment_program

Variable Name: Provider_Key
Variable Label: Provider Key
Description: Random unique key assigned to each row.

Variable Name: Practice_State_or_US_territory
Variable Label: Practice State or US territory
Description: The State or United States (US) territory code location of the TIN associated with the clinician.

Variable Name: Practice_Size
Variable Label: Practice Size
Description: Count of clinicians associated with TIN from the second segment of the MIPS eligibility determination period.

Variable Name: Clinician_Specialty
Variable Label: Clinician Specialty
Description: The specialty description is an identifier corresponding to the type of service that the clinician submitted most on their Medicare Part B claims for this TIN/NPI combination.

Variable Name: Years_in_Medicare
Variable Label: Years in Medicare
Description: The number of years since the first date an enrollment was approved for this NPI across all enrollments in PECOS.

Variable Name: NPI
Variable Label: NPI
Description: The National Provider Identifier assigned to the clinician when they enrolled in Medicare. Multiple rows for the same NPI indicate multiple TIN/NPI combinations.

Variable Name: Engaged
Variable Label: Engaged
Description: Indicates if the clinician reported a minimum of one measure or activity as an individual or group, or participated in a MIPS APM.

Variable Name: Participation_Type
Variable Label: Participation Type
Description: Indicates the level at which performance data was collected, submitted, or reported for the final score attributed to the clinician. All data elements from this point forward are based on the Participation Type identified in the preceding column (column 8).

Variable Name: Medicare_Patients
Variable Label: Medicare Patients
Description: The number of Medicare patients who received covered professional services during one segment of the MIPS eligibility determination period that was attributed to the participation type associated with the clinician's final score.

Variable Name: Allowed_Charges
Variable Label: Allowed Charges
Description: The allowed charges under the Physician Fee Schedule on Medicare Part B claims with a service date during one segment of the MIPS eligibility determination period that was attributed to the participation type associated with the clinician's final score.

Variable Name: Services
Variable Label: Services
Description: The number of covered professional services provided to Medicare Part B patients with a service date during one segment of the MIPS eligibility determination period that was attributed to the participation type associated with the clinician's final score.

Variable Name: Opted_Into_MIPS
Variable Label: Opted Into MIPS
Description: Indicates if an "opt-in eligible" clinician, group, or APM Entity elected to participate in MIPS and receive a payment adjustment. This status is attributed to the participation type associated with the clinician's final score.

Variable Name: Small_Practitioner
Variable Label: Small Practitioner
Description: Indicates if the clinician, group, or APM Entity had the small practice special (15 or fewer clinicians billed under the TIN or APM Entity) based on either segment of the MIPS eligibility determination period. Note: This number can contradict the practice size in column 3, which is always based on the 2nd segment.

Variable Name: Rural_Clinician
Variable Label: Rural Clinician
Description: Indicates if the clinician or group had the rural special status (practiced in a ZIP code designated as rural by the Federal Office of Rural Health Policy (FORHP) using the most recent FORHP Eligible ZIP code file available).

Variable Name: HPSA_Clinician
Variable Label: HPSA Clinician
Description: Indicates if the clinician or group had the HPSA special status (practiced in a Health Professional Shortage Area (HPSA)).

Variable Name: Ambulatory_Surgical_Center
Variable Label: Ambulatory Surgical Center
Description: Indicates if the clinician or group had the ambulatory surgical center-based special status (determined by the volume of their covered professional services furnished in an ambulatory surgical center). This status is attributed to the participation type associated with the clinician's final score.

Variable Name: HospitalBased_Clinician
Variable Label: HospitalBased Clinician
Description: Indicates if the clinician or group had the hospital-based special status (determined by the volume of their covered professional services furnished in a hospital setting). This status is attributed to the participation type associated with the clinician's final score.

Variable Name: Non-Patient_Facing
Variable Label: Non-Patient Facing
Description: Indicates if the clinician or group has the facility-based special status (based on the volume of services furnished in a facility eligible for the Hospital Value-based Purchasing program). This status is attributed to the participation type associated with the clinician's final score.

Variable Name: FacilityBased
Variable Label: FacilityBased
Description: Indicates if the clinician or group has the facility-based special status (based on the volume of services furnished in a facility eligible for the Hospital Value-based Purchasing program). This status is attributed to the participation type associated with the clinician's final score.

Variable Name: Extreme_Hardship
Variable Label: Extreme Hardship
Description: Indicates if the clinician or group was affected by an extreme and uncontrollable circumstance (EUC) (such as FEMA-designated major disaster) and qualified for performance category reweighting because of the MIPS automatic EUC policy or MIPS EUC exception application. This indicator is attributed to the participation type associated with the clinician's final score.

Variable Name: Final_Score
Variable Label: Final Score
Description: The MIPS final score attributed to the clinician (the highest final score that could be attributed to the clinician's TIN/NPI combination). This is based on the participation type associated with the clinician's final score.

Variable Name: Payment_Adjustment
Variable Label: Payment Adjustment
Description: The total payment adjustment attributed to the clinician for the 2022 payment year. Payment adjustments are determined by comparing the final score to the performance thresholds and then scaled to ensure budget neutrality.

Variable Name: Complex_Patient_Bonus
Variable Label: Complex Patient Bonus
Description: The complex patient bonus associated with the final score attributed to the clinician.

Variable Name: Extreme_Hardship_Quality
Variable Label: Extreme Hardship Quality
Description: Indicates if the clinician, group, or APM Entity was approved for reweighting of the quality performance category due to extreme and uncontrollable circumstances. This indicator is attributed to the participation type associated with the clinician's final score.

Variable Name: Quality_Category_Score
Variable Label: Quality Category Score
Description: This is the unweighted score received for the quality score that is used for the overall score.

Variable Name: Quality_Bonus
Variable Label: Quality Bonus
Description: The bonus points received for the quality category (small practice bonus and quality improvement, if applicable).

Variable Name: Quality_Measure_ID_X
Variable Label: Quality Measure ID X
Description: MIPS Quality ID for one of the quality measures that contributed to the final score.

Variable Name: Quality_Measure_Score_X
Variable Label: Quality Measure Score X
Description: Measure score (including bonus points) achieved for the corresponding MIPS Quality ID that contributed to the final score.

Variable Name: Promoting_Interoperability_(PI)_Category_score
Variable Label: Promoting Interoperability (PI) Category score
Description: This is the unweighted score received by the participant for the Promoting Interoperability category that is used for the overall score.

Variable Name: Extreme_Hardship_PI
Variable Label: Extreme Hardship PI
Description: Indicates if the clinician, group, or APM Entity was approved for reweighting of the Promoting Interoperability performance category due to extreme and uncontrollable circumstances.

Variable Name: PI_Hardship
Variable Label: PI Hardship
Description: Indicates if the clinician or group was approved for an exception from the Promoting Interoperability performance category due to participation in a small practice, decertified Electronic Health Record (EHR) technology, insufficient Internet connectivity, or lack of control over the availability of certified EHR technology (CEHRT).

Variable Name: PI_Reweighting
Variable Label: PI Reweighting
Description: Indicates if the clinician or group qualified for an automatic reweighting from the Promoting Interoperability performance category due to special status or clinician specialty.

Variable Name: PI_Bonus_
Variable Label: PI Bonus
Description: The total bonus points received by the clinician, group, or APM Entity for the Promoting Interoperability performance category.

Variable Name: PI_CEHRT_ID_(measurem_ent_set__cehrt_id)
Variable Label: PI CEHRT ID (measurement_set_cehrt_id)
Description: This is a unique identifier generated by the Office of the National Coordinator for Health Information Technology (ONC) and identifies a specific bundle of software or EHR. The CEHRT ID is a 15-character alphanumeric string which can be found on the CHPL website. This is the CEHRT ID included in the data that contributed to the clinician's final score.

Variable Name: PI_Measure_ID_X
Variable Label: PI Measure ID X
Description: MIPS Promoting Interoperability ID for one of the Promoting Interoperability measures that contributed to the final score.

Variable Name: PI_Measure_Score_X
Variable Label: PI Measure Score X
Description: Measure score achieved for the corresponding MIPS Promoting Interoperability ID that contributed to the final score.

Variable Name: IA_Score
Variable Label: IA Score
Description: The score received for the improvement activities performance category based on all the activities picked for the category that contributed to the final score.

Variable Name: Extreme_Hardship_IA
Variable Label: Extreme Hardship IA
Description: Indicates if the clinician, group, or APM Entity was approved for reweighting of the improvement activities performance category due to extreme and uncontrollable circumstances.

Variable Name: IA_Study
Variable Label: IA Study
Description: This data element will show as FALSE for everyone because this study concluded after the 2019 performance year.

Variable Name: IA_Measure_ID_X
Variable Label: IA Measure ID X
Description: MIPS Improvement Activity ID for one of the improvement activities that contributed to the final score.

Variable Name: IA_Measure_Score_X
Variable Label: IA Measure Score X
Description: Activity score achieved for the corresponding MIPS Improvement Activity ID that contributed to the final score.

Variable Name: Cost_Score
Variable Label: Cost Score
Description: The unweighted score received for the cost performance category based on all the cost measures used for final scoring. Will display as '0' for all clinicians because cost was reweighted in the 2020 performance year.

Variable Name: Extreme_Hardship_Cost
Variable Label: Extreme Hardship Cost
Description: Indicates if the clinician was approved for reweighting of the cost performance category due to extreme and uncontrollable circumstances. (Not applicable (N/A) for 2020; this category was 
reweighted for all individuals and groups.)

Variable Name: Cost_Measure_ID_X
Variable Label: Cost Measure ID X
Description: MIPS Cost ID for one of the cost measures that contributed to the final score. (N/A for 2020; this category was reweighted for all individuals and groups.)

Variable Name: Cost_Measure_Score_X
Variable Label: Cost Measure Score X
Description: Cost score achieved for the corresponding MIPS Cost ID that contributed to the final score. (N/A for 2020; this category was reweighted for all individuals and groups.)

--------------------------------
Convert this natural language query into SQL based on the tables defined above in the database: 
"""

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
            prompt = openai_prompt + input_text + "\n\ Use limit clause to only return a maximum of 100 rows and write the SQL in the postgresql syntax.\nSQL:"
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

if __name__ == '__main__':
    app.run(debug=True)
