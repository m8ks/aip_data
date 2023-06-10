import json
from json import JSONDecodeError
import streamlit as st
import pandas as pd

import re
from aip_db import *
import streamlit.components.v1 as stc
from st_on_hover_tabs import on_hover_tabs
from streamlit.runtime.runtime import Runtime, SessionInfo
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.web.server.server import Server
from datetime import datetime, timedelta
import base64
import extra_streamlit_components as stx

cookie_name = 'streamlit_cookie'


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


def save_cookie(userid, password, role, schema, database, account, warehouse):
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    minutes = config['cookie']['expiry_minutes']
    expire = datetime.now() + timedelta(minutes=minutes)
    value = expire.strftime("%Y-%m-%d %H:%M:%S")
    streamlit_cookie = {
        "userid": userid,
        "password": password,
        "role": role,
        "expire": value,
        "schema": schema,
        "database": database,
        "account": account,
        "warehouse": warehouse
    }
    json_string = json.dumps(streamlit_cookie)
    message_bytes = json_string.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    get_manager().set(cookie_name, base64_message, expires_at=datetime.max)


def get_cookie_values():
    user_value, password_value, role_value, expire_value, schema_value, database_value, account_value, warehouse_value \
        = None, None, None, None, None, None, None, None

    json_data = get_manager().get(cookie_name)

    if json_data:
        base64_bytes = json_data.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        streamlit_cookie = json.loads(message)
        try:
            user_value = streamlit_cookie['userid']
            password_value = streamlit_cookie['password']
            role_value = streamlit_cookie['role']
            expire_value = streamlit_cookie['expire']
            schema_value = streamlit_cookie['schema']
            database_value = streamlit_cookie['database']
            account_value = streamlit_cookie['account']
            warehouse_value = streamlit_cookie['warehouse']
        except JSONDecodeError:
            pass

    return [user_value, password_value, role_value, expire_value, schema_value, database_value, account_value,
            warehouse_value]


sf = Snowflake()
cookie_manager = get_manager()
cookie_manager.get_all()

[userid, password, role, value, schema, database, account, warehouse] = get_cookie_values()

if schema:
    schema_str = schema + ", version 2.0"
else:
    schema_str = "version 2.0"

html_banner = ("    \n"
               "    <div style=\"background-color:#0B074E;padding:16px;border-radius:10px\">\n"
               "        <img src=\"https://www.aip.org/sites/default/files/aip-logo-180.png\">\n"
               "        <h1 style=\"color:white;"
               "            text-align:center;"
               "            font-family:Trebuchet MS, sans-serif;\">FYI Budget Tracker "
               "        </h1>\n"
               "        <h2 style=\"color:white;"
               "            text-align:center;"
               "            font-family:Trebuchet MS, sans-serif;\">" + schema_str + ""
               "        </h2>\n"
               "    </div>\n"
               "    ")

stc.html(html_banner, height=225)

# Config
# st.set_page_config(page_title='Bulk upload', page_icon='📤', layout='wide')

# Style
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Title
st.title('📤 Bulk upload')


expire = datetime.now()

if value is not None:
    expire = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

# st.info(value)

if expire < datetime.now():
    if cookie_manager.get(cookie_name):
        cookie_manager.delete(cookie_name)
    userid = ''
    password = ''
    role = ''

if userid is None:
    userid = ''

if password is None:
    password = ''

if userid != '' and password != '':
    try:
        sf.authorization(userid, password, role, schema, database, account, warehouse)
        save_cookie(userid, password, role, schema, database, account, warehouse)
    except Exception as e:
        st.error(str(e))

if sf.not_connected():
    st.subheader('🧑‍💻 Authorization')

    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    sf_account = config['snowflake']['account']
    sf_database = config['snowflake']['database']
    sf_schema = config['snowflake']['schema']
    sf_warehouse = config['snowflake']['warehouse']
    sf_role = config['snowflake']['role']

    userid = st.text_input('Username').lower()
    password = st.text_input('Password', type="password")
    role = st.selectbox('Snowflake role',
                        sf_role,
                        index=2,
                        disabled=False)  # True)

    col1, col2 = st.columns(2)

    with col1:
        st.text_input('Snowflake database', sf_database, disabled=True)
        st.text_input('Snowflake account', sf_account, disabled=True)
    with col2:
        select_schema = st.selectbox('Snowflake schema', sf_schema, index=3)
        st.text_input('Snowflake warehouse', sf_warehouse, disabled=True)

    if st.button('Login'):
        if userid == '' or password == '':
            st.warning('Please provide account and password to login.')
        else:
            try:
                sf.authorization(userid, password, role, select_schema, sf_database, sf_account,
                                 sf_warehouse)  # sf_schema[2]
                save_cookie(userid, password, role, select_schema, sf_database, sf_account,
                            sf_warehouse)  # sf_schema[2]
                --st.experimental_rerun()
            except Exception as e:
                st.error(str(e))
else:
    # st.subheader('📤 Bulk upload')
    st.info('You can use bulk upload by selecting the csv file, \n'
            'please verify the data and push it into the Preview table by clicking \'Submit\' button')

    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    delimiter = config['file_upload']['delimiter']
    uploaded_file = st.file_uploader('Upload CSV', type='.csv')

    if uploaded_file:
        try:
            csv_df = pd.read_csv(uploaded_file,
                                 delimiter=delimiter,  # ';',
                                 header=None,
                                 names=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION',
                                        'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE'],
                                 dtype={'FUNDING_LINE_ID': int, 'FISCAL_YEAR': int, 'STEP': str,
                                        'AMOUNT': float, 'AMOUNT_TYPE': str, 'SOURCE_URL': str,
                                        'NOTE': str},
                                 skiprows=1)

            # with st.expander('File data preview'):
            csv_df = pd.DataFrame(csv_df,
                                  columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE',
                                           'VERSION',
                                           'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                           'SOURCE_URL',
                                           'NOTE']
                                  )

            st.dataframe(csv_df)

            st.write('')
            st.write('### Upload from ', uploaded_file.name)
            st.write('')

            if st.button('Submit'):

                if not csv_df.empty:

                    # sf.delete_funding_amount_upload(userid=userid)

                    for row in csv_df.itertuples():
                        funding_line_id = row.FUNDING_LINE_ID
                        fiscal_year = row.FISCAL_YEAR
                        step = row.STEP
                        amount = row.AMOUNT
                        amount_type = row.AMOUNT_TYPE
                        source_url = row.SOURCE_URL
                        note = row.NOTE

                        df_amount_upload = sf.exist_funding_amount_upload(userid, funding_line_id, fiscal_year,
                                                                          step, amount_type)
                        df_amount_upload = pd.DataFrame(df_amount_upload)

                        if not df_amount_upload.empty:
                            sf.update_funding_amount_upload(userid, funding_line_id, int(fiscal_year), step,
                                                            amount_type, int(fiscal_year), step, amount,
                                                            amount_type, source_url, note)
                            st.warning("Existing FUNDING AMOUNT PREVIEW was updated for '{}': "
                                       "FUNDING_LINE_ID = '{}', "
                                       "FISCAL_YEAR = {}, STEP = '{}', "
                                       "AMOUNT_TYPE = '{}' ".format(userid, funding_line_id, int(fiscal_year),
                                                                    step, amount_type))
                        else:
                            sf.insert_funding_amount_upload(userid, funding_line_id, int(fiscal_year), step,
                                                            amount, amount_type, source_url, note)
                            st.info("New record added to FUNDING AMOUNT PREVIEW for '{}': "
                                    "FUNDING_LINE_ID = '{}', "
                                    "FISCAL_YEAR = {}, "
                                    "STEP = '{}', "
                                    "AMOUNT_TYPE = '{}'".format(userid, funding_line_id, fiscal_year,
                                                                step, amount_type))

                        # sf.insert_funding_amount_upload(funding_line_id, int(fiscal_year), step, amount,
                        #                                 amount_type,
                        #                                 source_url, note, userid)
                        # st.info("New record added to FUNDING AMOUNT PREVIEW: "
                        #         "FUNDING_LINE_ID = '{}', "
                        #         "FISCAL_YEAR = {}, "
                        #         "STEP = '{}', "
                        #         "AMOUNT_TYPE = '{}', "
                        #         "USER = '{}'".format(funding_line_id, fiscal_year, step, amount_type, userid))

                    st.success('Upload was successfully completed.')
                    st.experimental_rerun()

        except Exception as e:
            st.error(str(e))