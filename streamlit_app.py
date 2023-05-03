import json
import logging
from json import JSONDecodeError
import streamlit as st
import pandas as pd
import yaml

from aip_db import *
import streamlit.components.v1 as stc
from st_on_hover_tabs import on_hover_tabs
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import base64

cookie_name = '_streamlit_csrf'
HTML_BANNER = ("    \n"
               "    <div style=\"background-color:#0B074E;padding:16px;border-radius:10px\">\n"
               "        <img src=\"https://www.aip.org/sites/default/files/aip-logo-180.png\">\n"
               "        <h1 style=\"color:white;"
               "            text-align:center;"
               "            font-family:Trebuchet MS, sans-serif;\">Snowflake Data Management"
               "        </h1>\n"
               "        <h2 style=\"color:white;"
               "            text-align:center;"
               "            font-family:Trebuchet MS, sans-serif;\">version 1.2"
               "        </h2>\n"
               "    </div>\n"
               "    ")
@st.cache(allow_output_mutation=True)
def get_manager():
    stx.IS_RELEASE = False
    return stx.CookieManager()


cookie_manager = get_manager()

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
    cookie_manager.set(cookie_name, base64_message)

def get_cookie_values():
    user_value, password_value, role_value, expire_value, schema_value, database_value, account_value, warehouse_value \
        = None, None, None, None, None, None, None, None

    json_data = cookie_manager.get(cookie_name)

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

    return [user_value, password_value, role_value, expire_value, schema_value, database_value, account_value, warehouse_value]


def main():
    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)
    stc.html(HTML_BANNER, height=225)
    cookie_manager.get_all()
    logging.info(stx.IS_RELEASE)
    sf = Snowflake()

    [userid, password, role, value, schema, database, account, warehouse] = get_cookie_values()

    st.info(schema)
    st.info(database)
    st.info(account)
    st.info(warehouse)

    expire = datetime.now()

    if value is not None:
        expire = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

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
        userid = st.text_input('Username').lower()
        password = st.text_input('Password', type="password")
        role = st.selectbox('Snowflake role',
                            ('PUBLIC', 'ACCOUNTADMIN', 'FYI_BUDGET_TRACKER_DB_ADMIN_ROLE'),
                            index=2,
                            disabled=False)  # True)

        col1, col2 = st.columns(2)

        with open("config.yaml") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        sf_account = config['snowflake']['account']
        sf_database = config['snowflake']['database']
        sf_schema = config['snowflake']['schema']
        sf_warehouse = config['snowflake']['warehouse']

        with col1:
            st.text_input('Snowflake database', sf_database, disabled=True)
            st.text_input('Snowflake account', sf_account, disabled=True)
        with col2:
            st.selectbox('Snowflake schema', sf_schema, index=2)
            st.text_input('Snowflake warehouse', sf_warehouse, disabled=True)

        if st.button('Login'):
            if userid == '' or password == '':
                st.warning('Please provide account and password to login.')
            else:
                try:
                    sf.authorization(userid, password, role, sf_schema[2], sf_database, sf_account, sf_warehouse)
                    save_cookie(userid, password, role, sf_schema[2], sf_database, sf_account, sf_warehouse)
                    st.experimental_rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        with st.sidebar:
            tabs = on_hover_tabs(
                tabName=['Home', 'Organization', 'Funding Line', 'Edit Line', 'Funding Amount', 'Bulk download',
                         'Bulk upload', 'Sync all', 'Logout', 'About'],
                iconName=['home', 'table', 'table', 'edit', 'table', 'download', 'upload', 'cloud_sync', 'logout'],
                default_choice=0,
                styles={'navtab': {'background-color': '#111',
                                   'color': '#818181',
                                   'font-size': '16px',
                                   'transition': '.3s',
                                   'white-space': 'nowrap',
                                   'text-transform': 'uppercase'},
                        'tabOptionsStyle': {':hover :hover': {'color': 'white',
                                                              'cursor': 'pointer'}},
                        'iconStyle': {'position': 'fixed',
                                      'left': '7.5px',
                                      'text-align': 'left'},
                        'tabStyle': {'list-style-type': 'none',
                                     'margin-bottom': '30px',
                                     'padding-left': '30px'}},
                key="1")

        if tabs == 'Home':
            st.subheader('🏠 Home page')

            st.info('Here is a Script - you can use the UAT database for testing:\n'
                    '1) Login\n'
                    '2) Org - use the drill down tool to look up Orgs (and children), add an Org\n'
                    '3) Funding Line Item - use the drill down tool to look up a Funding Line Item, add a Funding '
                    'Line Item, and Edit a Funding Line Item\n '
                    '4) Funding Amount - use drill down to look up Funding Amounts, Add new record\n'
                    '5) Funding Amount - Bulk Download - filter to items to download, choose empty field option and '
                    'then repeat with populated field option - verify that a csv file is downloaded to your computer '
                    'each time with expected format and columns populated\n '
                    '6) Funding Amount - Bulk Upload - Use one of csv files downloaded in step 5 (or both) - edit the '
                    'contents - upload - verify that data is placed in the Preview table\n '
                    '7) Synchronize - view bulk uploaded data - verify user name - go back to step 6 and alter a line '
                    'in the csv file - re-upload - verify that the previous Preview data is replaced by the new '
                    'upload - submit - verify data has either been added or updated existing data in Funding Amounts '
                    'table (step 4)\n '
                    '8) Log out (Sign out) and Log back in')

        elif tabs == 'Organization':
            st.subheader('🏢 Organization list')

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
                name = st.text_input('NAME', 'Dummy name')

            if st.button('Submit'):
                df_org_ids = pd.DataFrame(sf_org_ids)

                if org_id in set(df_org_ids.values[:, 0]):
                    st.error("ORGANIZATION is already exists: ORG_ID = '{}' ".format(org_id))
                else:
                    sf.insert_organization(org.upper(), parent, org_id, int(level), name)
                    st.success("New record added to ORGANIZATION: ORG_ID = '{}'".format(org_id))
                    st.experimental_rerun()

        elif tabs == 'Funding Line':
            st.subheader('📁 Funding Line list')

            sf_line = sf.view_data_funding_line()
            df_line = pd.DataFrame(sf_line,
                                   columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])

            col1, col2 = st.columns(2)
            with col1:
                sf_org_ids = sf.view_all_org_ids()
                select_org = st.multiselect("Select ORG_ID:", [str(i[0]) for i in sf_org_ids])
                # sf_select_org = sf.view_data_organization(select_org)
                # df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
            with col2:
                select_name = st.multiselect("Select NAME:", set(df_line['NAME']))

            df_selected = sf.view_data_funding_line(df_org=select_org, df_name=select_name)
            df_selected = pd.DataFrame(df_selected,
                                       columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
            st.dataframe(df_selected,
                         use_container_width=True)

            st.subheader('➕ Add new record')
            col1, col2 = st.columns(2)

            with col1:
                last_row = sf.get_last_row_funding_line()
                last_row = pd.DataFrame(last_row)
                # st.info(last_row[0].values)
                st.text_input('ID', int(last_row[0].values + 1), disabled=True)
                list_of_records = [i[0] for i in sf_org_ids]
                org_id = st.selectbox('ORG_ID', list_of_records)
                name = st.text_input('NAME', 'Dummy name')

            with col2:
                funding_type = st.text_input('FUNDING_TYPE', 'Dummy funding type')
                version = st.number_input('VERSION', 0)
                top_line = st.selectbox('TOP_LINE', ('FALSE', 'TRUE'))
                note = st.text_area('NOTE', 'Dummy note')

            if st.button('Submit'):
                sf_line = sf.exists_funding_line(org_id, name, version)
                df_line = pd.DataFrame(sf_line)

                if not df_line.empty:
                    st.error("FUNDING LINE is already exists: ORG_ID = '{}', NAME = '{}', VERSION = {} ".format(
                        org_id, name, version))
                else:
                    sf.insert_funding_line(int(last_row[0].values + 1), org_id, name, funding_type, version,
                                           top_line, note)
                    st.success("New record added to FUNDING LINE: ORG_ID = '{}', NAME = '{}', VERSION = {}".format(
                        org_id, name, version))
                    st.experimental_rerun()

        elif tabs == 'Edit Line':
            st.subheader('📁 Edit Funding Line')

            # sf_line = sf.view_data_funding_line()
            df_line = pd.DataFrame(sf.view_data_funding_line(),
                                   columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])

            col1, col2 = st.columns(2)
            with col1:
                # sf_org_ids = sf.view_all_org_ids()
                # df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
                select_org = st.multiselect("Select ORG_ID:", [str(i[0]) for i in sf.view_all_org_ids()])
            with col2:
                select_name = st.multiselect("Select NAME:", set(df_line['NAME']))

            # sf_selected = sf.view_data_funding_line(select_org, select_name)
            df_selected = pd.DataFrame(sf.view_data_funding_line(select_org, select_name),
                                       columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
            st.dataframe(df_selected,
                         use_container_width=True)

            df_line_id = st.selectbox("Select ID:", set(df_selected['ID']))
            df_selected = pd.DataFrame(sf.view_data_funding_line(None, None, df_line_id),
                                       columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
            st.dataframe(df_selected, use_container_width=True)

            st.subheader('✏️ Edit record')
            col1, col2 = st.columns(2)

            with col1:
                id = st.text_input('ID', df_selected['ID'][0], disabled=True)
                list_of_records = [i[0] for i in sf.view_all_org_ids()]

                # org_id = st.selectbox('ORG_ID', list_of_records, index=0)
                org_id = st.text_input('ORG_ID', df_selected['ORG_ID'][0], disabled=True)
                name = st.text_input('NAME', df_selected['NAME'][0])

            with col2:
                funding_type = st.text_input('FUNDING_TYPE', df_selected['FUNDING_TYPE'][0])
                version = st.number_input('VERSION', df_selected['VERSION'][0])
                top_line = st.selectbox('TOP_LINE', ('FALSE', 'TRUE'), bool(df_selected['TOP_LINE'][0]))
                note = st.text_area('NOTE', df_selected['NOTE'][0])

            if st.button('Submit'):
                sf.update_funding_line(id, org_id, name, funding_type, version, top_line, note)
                st.success("Existing FUNDING LINE record was updated: "
                           "ID = {}, ORG_ID = '{}', NAME = '{}', FUNDING_TYPE = '{}', VERSION = {}, TOP_LINE = {}, "
                           "NOTE = '{}' ".format(
                    id, org_id, name, funding_type, version, top_line, note))
                st.experimental_rerun()

        elif tabs == 'Funding Amount':
            st.subheader('💵 Funding Amount list')

            df_amount = pd.DataFrame(sf.view_data_funding_amount(),
                                     columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION',
                                              'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE']
                                     )

            col1, col2 = st.columns(2)
            with col1:
                # df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
                select_org = st.multiselect("Select ORG_ID:", [str(i[0]) for i in sf.view_all_org_ids()])
                select_name = st.multiselect("Select NAME:", set(df_amount['NAME']))
            with col2:
                select_year = st.multiselect("Select FISCAL_YEAR:", set(df_amount['FISCAL_YEAR']))
                select_step = st.multiselect("Select STEP:", set(df_amount['STEP']))

            df_selected = sf.view_data_funding_amount(df_org=select_org,
                                                      df_name=select_name,
                                                      df_year=select_year,
                                                      df_step=select_step)
            df_selected = pd.DataFrame(df_selected,
                                       columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION',
                                                'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE']
                                       )
            st.dataframe(df_selected,
                         use_container_width=True)

            st.subheader('➕ Add new record')
            col1, col2 = st.columns(2)

            with col1:
                list_of_records = [i[0] for i in sf.view_all_funding_ids()]
                funding_line_id = st.selectbox('FUNDING_LINE_ID',
                                               set(df_selected['FUNDING_LINE_ID']))  # list_of_records)
                fiscal_year = st.selectbox('FISCAL_YEAR',
                                           ('2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017',
                                            '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025',
                                            '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033',
                                            '2034', '2035', '2036', '2037', '2038', '2039', '2040', '2041',
                                            '2042', '2043', '2044', '2045', '2046', '2047', '2048', '2049',
                                            '2050', '2051', '2052', '2053', '2054', '2055', '2056', '2057',
                                            '2058', '2059', '2060', '2061', '2062', '2063', '2064', '2065',
                                            '2066', '2067', '2068', '2069', '2070', '2071', '2072', '2073',
                                            '2074', '2075', '2076', '2077', '2078', '2079', '2080', '2081',
                                            '2082', '2083', '2084', '2085', '2086', '2087', '2088', '2089',
                                            '2090', '2091', '2092', '2093', '2094', '2095', '2096', '2097',
                                            '2098', '2099'),
                                           index=13)
                step = st.selectbox('STEP', ('Request', 'House', 'Senate', 'Enacted'))

            with col2:
                amount = st.number_input('AMOUNT')
                amount_type = st.text_input('AMOUNT_TYPE', 'Dummy amount type')
                source_url = st.text_input('SOURCE_URL', 'Dummy source url')
                note = st.text_area('NOTE', 'Dummy note')

            if st.button('Submit'):
                df = sf.exists_funding_amount(funding_line_id, int(fiscal_year), step, amount_type)
                df = pd.DataFrame(df)

                if not df.empty:
                    st.error("FUNDING AMOUNT is already exists: FUNDING_LINE_ID = '{}', FISCAL_YEAR = {}, STEP = '{}', "
                             "AMOUNT_TYPE = '{}' ".format(funding_line_id, int(fiscal_year), step, amount_type))
                else:
                    sf.insert_funding_amount(funding_line_id, int(fiscal_year), step, amount, amount_type,
                                             source_url, note)
                    st.success("New record added to FUNDING AMOUNT: "
                               "FUNDING_LINE_ID = '{}', "
                               "FISCAL_YEAR = {}, "
                               "STEP = '{}', "
                               "AMOUNT_TYPE = '{}'".format(funding_line_id, fiscal_year, step, amount_type))
                    st.experimental_rerun()

        elif tabs == 'Bulk download':
            st.subheader('📥 Bulk download')

            df_amount = pd.DataFrame(sf.view_data_funding_amount(isblank=False),
                                     columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION',
                                              'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE']
                                     )

            # df_org = sf.view_data_organization()
            # df_org = pd.DataFrame(sf.view_data_organization(), columns=['ORG_ID', 'PARENT', ])

            col1, col2 = st.columns(2)

            with col1:
                # df_org = st.multiselect("Select ORG_ID:", df_org['ORG_ID'])  # set(df['ORG_ID']))
                select_org = st.multiselect("Select ORG_ID:", [str(i[0]) for i in sf.view_all_org_ids()])
                select_name = st.multiselect("Select NAME:", set(df_amount['NAME']))
                select_isblank = st.checkbox("Download with blank values?")
            with col2:
                select_year = st.multiselect("Select FISCAL_YEAR:", set(df_amount['FISCAL_YEAR']))
                select_step = st.multiselect("Select STEP:", set(df_amount['STEP']))

            df_selected = sf.view_data_funding_amount(isblank=select_isblank,
                                                      df_org=select_org,
                                                      df_name=select_name,
                                                      df_year=select_year,
                                                      df_step=select_step)
            df_selected = pd.DataFrame(df_selected,
                                       columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION',
                                                'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE']
                                       )
            st.dataframe(df_selected,
                         use_container_width=True)

            @st.experimental_memo
            def convert_df(df_csv):
                return df_csv.to_csv(index=False).encode('utf-8')

            csv = convert_df(pd.DataFrame(sf.view_data_funding_amount(isblank=select_isblank,
                                                                      df_org=select_org,
                                                                      df_name=select_name,
                                                                      df_year=select_year,
                                                                      df_step=select_step),
                                          columns=['FUNDING_LINE_ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION',
                                                   'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE']
                                          ))

            if st.download_button(
                    "Press to Download",
                    csv,
                    "funding_amount.csv",
                    "text/csv",
                    key='download-csv'
            ):
                st.success('The file successfully downloaded.')

        elif tabs == 'Bulk upload':
            st.subheader('📤 Bulk upload')

            uploaded_file = st.file_uploader('Upload CSV', type='.csv')

            if uploaded_file:
                try:
                    csv_df = pd.read_csv(uploaded_file,
                                         delimiter=';',
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

                            sf.delete_funding_amount_upload(userid=userid)

                            for row in csv_df.itertuples():
                                funding_line_id = row.FUNDING_LINE_ID
                                fiscal_year = row.FISCAL_YEAR
                                step = row.STEP
                                amount = row.AMOUNT
                                amount_type = row.AMOUNT_TYPE
                                source_url = row.SOURCE_URL
                                note = row.NOTE

                                # df_amount = sf.exists_funding_amount(funding_line_id, int(fiscal_year), step,
                                #                                      amount_type)
                                # df_amount = pd.DataFrame(df_amount)

                                # if not df_amount.empty:
                                #     sf.update_funding_amount(funding_line_id, int(fiscal_year), step,
                                #                              amount_type,
                                #                              int(fiscal_year), step, amount,
                                #                              amount_type, source_url, note)
                                #     st.warning("Existing FUNDING AMOUNT record was updated: "
                                #                "FUNDING_LINE_ID = '{}', "
                                #                "FISCAL_YEAR = {}, STEP = '{}', "
                                #                "AMOUNT_TYPE = '{}' ".format(
                                #         funding_line_id, int(fiscal_year), step, amount_type))
                                # else:
                                #     sf.insert_funding_amount(funding_line_id, int(fiscal_year), step, amount,
                                #                              amount_type,
                                #                              source_url, note)
                                #     st.info("New record added to FUNDING AMOUNT: "
                                #             "FUNDING_LINE_ID = '{}', "
                                #             "FISCAL_YEAR = {}, "
                                #             "STEP = '{}', "
                                #             "AMOUNT_TYPE = '{}'".format(
                                #         funding_line_id, fiscal_year, step, amount_type))

                                sf.insert_funding_amount_upload(funding_line_id, int(fiscal_year), step, amount,
                                                                amount_type,
                                                                source_url, note, userid)
                                st.info("New record added to FUNDING AMOUNT PREVIEW: "
                                        "FUNDING_LINE_ID = '{}', "
                                        "FISCAL_YEAR = {}, "
                                        "STEP = '{}', "
                                        "AMOUNT_TYPE = '{}', "
                                        "USER = '{}'".format(funding_line_id, fiscal_year, step, amount_type, userid))

                            st.success('Upload was successfully completed.')
                except Exception as e:
                    st.error(str(e))

        elif tabs == 'Sync all':
            st.subheader('☁️ Review and push to database')

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
                for row in df_selected.itertuples():
                    funding_line_id = row.FUNDING_LINE_ID
                    fiscal_year = row.FISCAL_YEAR
                    step = row.STEP
                    amount = row.AMOUNT
                    amount_type = row.AMOUNT_TYPE
                    source_url = row.SOURCE_URL
                    note = row.NOTE

                    df_amount = pd.DataFrame(sf.exists_funding_amount(funding_line_id, int(fiscal_year), step,
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

                st.success('Upload was successfully completed.')

        elif tabs == 'Logout':
            cookie_manager.delete(cookie_name)
            st.experimental_rerun()

        else:
            st.subheader('About')
            st.info('Build for AIP.ORG by Dmitry Taranenko@dPrism')


if __name__ == '__main__':
    main()
