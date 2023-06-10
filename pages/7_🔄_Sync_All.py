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
# st.set_page_config(page_title='Review and push to database', page_icon='🔄️', layout='wide')

# Style
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Title
st.title('🔄️ Review and push into Snowflake')


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
    # st.subheader('☁️ Review and push to database')
    st.info('How to synchronize? \n'
            '- View bulk uploaded data \n'
            '- Verify user name \n'
            '- Go back to Bulk upload and alter a line in '
            'the csv file and then re-upload \n'
            '- Verify that the previous Preview data is replaced by the new upload \n'
            '- Submit \n'
            '- Verify data has either been added or updated existing data in Funding Amounts table')

    # df_upload = sf.view_data_funding_amount_upload()
    df_upload = pd.DataFrame(sf.view_data_funding_amount_upload(extended=True),
                             columns=['USER', 'FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FISCAL_YEAR', 'STEP',
                                      'AMOUNT',
                                      'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE'])

    col1, col2 = st.columns(2)
    with col1:
        select_org = st.multiselect("Select ORG_ID:", set(df_upload['ORG_ID']))
        select_name = st.multiselect("Select NAME:", set(df_upload['NAME']))
        select_user = st.multiselect("Select USER:", set(df_upload['USER']))
        select_clear = st.checkbox("Clear all data in Preview table after sync?")
    with col2:
        select_year = st.multiselect("Select FISCAL_YEAR:", set(df_upload['FISCAL_YEAR']))
        select_step = st.multiselect("Select STEP:", set(df_upload['STEP']))

    df_selected = pd.DataFrame(sf.view_data_funding_amount_upload(extended=True,
                                                                  df_org=select_org,
                                                                  df_name=select_name,
                                                                  df_year=select_year,
                                                                  df_step=select_step,
                                                                  df_user=select_user),
                               columns=['USER', 'FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FISCAL_YEAR', 'STEP',
                                        'AMOUNT',
                                        'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE'])
    st.dataframe(df_selected,
                 use_container_width=True)

    if st.button('Submit'):

        if select_org == [] and select_name == [] and select_year == [] and select_step == []:
            st.warning('All items from Preview table will be pushed into database.. please wait')

        for row in df_selected.itertuples():
            funding_line_id = row.FUNDING_LINE_ID
            fiscal_year = row.FISCAL_YEAR
            step = row.STEP
            amount = row.AMOUNT
            amount_type = row.AMOUNT_TYPE
            source_url = row.SOURCE_URL
            note = row.NOTE

            df_amount = pd.DataFrame(sf.exist_funding_amount(funding_line_id, int(fiscal_year), step,
                                                             amount_type))

            if not df_amount.empty:
                sf.update_funding_amount(funding_line_id, int(fiscal_year), step,
                                         amount_type,
                                         int(fiscal_year), step, amount,
                                         amount_type, source_url, note)
                st.warning("Existing FUNDING AMOUNT record was updated: "
                           "FUNDING_LINE_ID = '{}', "
                           "FISCAL_YEAR = {}, STEP = '{}', "
                           "AMOUNT_TYPE = '{}' ".format(
                    funding_line_id, int(fiscal_year), step, amount_type))
            else:
                sf.insert_funding_amount(funding_line_id, int(fiscal_year), step, amount,
                                         amount_type,
                                         source_url, note)
                st.info("New record was added to FUNDING AMOUNT: "
                        "FUNDING_LINE_ID = '{}', "
                        "FISCAL_YEAR = {}, "
                        "STEP = '{}', "
                        "AMOUNT_TYPE = '{}'".format(
                    funding_line_id, fiscal_year, step, amount_type))

            if select_clear:
                sf.delete_funding_amount_upload(userid, funding_line_id, fiscal_year, step, amount_type)

        st.success('Upload was successfully completed.')
        st.experimental_rerun()

    if st.button('Clear'):
        if select_org == [] and select_name == [] and select_year == [] and select_step == []:
            st.warning('All items from Preview table will be purged.. please wait')

        for row in df_selected.itertuples():
            sf.delete_funding_amount_upload(userid, row.FUNDING_LINE_ID, row.FISCAL_YEAR, row.STEP, row.AMOUNT_TYPE)

        st.success('Purge was successfully completed.')
        st.experimental_rerun()