import json
from json import JSONDecodeError
import streamlit as st
import pandas as pd

from aip_db import *
import streamlit.components.v1 as stc
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


# Config
st.set_page_config(page_title='Organization list', page_icon='🏢', layout='wide')

# Style
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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

# Title
st.title('🏢 Organization list')

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
    # st.title('🧑‍💻 Authorization')

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
    # st.subheader('🏢 Organization list')

    sf_org = sf.view_data_organization()
    pd.DataFrame(sf_org, columns=['ORG', 'PARENT', 'ORG_ID', 'LEVEL', 'NAME'])

    sf_org_ids = sf.view_all_org_ids()
    select_org = st.multiselect("Select ORG_ID:", [str(i[0]) for i in sf_org_ids])
    sf_select_org = sf.view_child_org_ids(select_org)

    # if not df_selected.empty:
    #     st.dataframe(df_selected, use_container_width=True)
    # else:
    df_select_org = pd.DataFrame(sf_select_org,
                                 columns=['ORG', 'PARENT', 'ORG_ID', 'LEVEL', 'NAME'])
    st.dataframe(df_select_org,
                 use_container_width=True)

    st.subheader('➕ Add new record')
    col1, col2 = st.columns(2)

    with col1:
        org = st.text_input('ORG')
        list_of_records = ['<NA>'] + [str(i[0]) for i in sf_org_ids]
        parent = st.selectbox('PARENT', list_of_records, index=0)
        if parent == '<NA>':
            org_id = st.text_input('ORG_ID', disabled=True, value=org.upper())
        else:
            org_id = st.text_input('ORG_ID', disabled=True, value=parent + "-" + org.upper())

    with col2:
        if parent == '<NA>':
            parent_level = [-1]
        else:
            parent_level = sf.get_parent_level(parent)
        parent_level = pd.DataFrame(parent_level)
        level = st.text_input('LEVEL', int(parent_level[0].values + 1), disabled=True)
        name = st.text_input('NAME')  # , 'Dummy name')

    if st.button('Submit'):
        df_org_ids = pd.DataFrame(sf_org_ids)

        if org_id in set(df_org_ids.values[:, 0]):
            st.error("ORGANIZATION is already exists: ORG_ID = '{}' ".format(org_id))
        else:
            sf.insert_organization(org.upper(), parent, org_id, int(level), name)
            st.success("New record added to ORGANIZATION: ORG_ID = '{}'".format(org_id))
            st.experimental_rerun()