import streamlit as st
import pandas as pd
from aip_db import *
import streamlit.components.v1 as stc
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode
import streamlit_authenticator as stauth
from st_on_hover_tabs import on_hover_tabs
import numpy as np

# from snowflake.snowpark import Session
# import json
# from snowflake.snowpark.functions import col, call_builtin

HTML_BANNER = ("    \n"
               "    <div style=\"background-color:#0B074E;padding:10px;border-radius:10px\">\n"
               "    <img src=\"https://www.aip.org/sites/default/files/aip-logo-180.png\">\n"
               "    <h1 style=\"color:white;text-align:center;\">Snowflake Datа Management</h1>\n"
               "    <p style=\"color:white;text-align:center;\">Built with Streamlit</p>\n"
               "    </div>\n"
               "    ")


def main():
    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

    with st.sidebar:
        tabs = on_hover_tabs(
            tabName=['Login', 'Organization', 'Funding Line', 'Edit Line', 'Funding Amount', 'Bulk download',
                     'Bulk upload',
                     # 'Add/Edit',
                     'About'],
            iconName=['person', 'dashboard', 'money', '', 'money', '', '',
                      # '',
                      'person'],
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

    stc.html(HTML_BANNER)

    # choice2 = st.sidebar.selectbox('Table name',
    #                                ['AGENCYINFO', 'CHANGEOVERPRIORYEAR', 'CHARTLABELS', 'FUNDINGAMOUNTS', 'PRIORYEAR', 'WEBTABLEROWLABELS'],
    #                                index=3)

    # menu = ['Bulk upload', 'Bulk update', 'Bulk delete', 'View all', 'Create record', 'Update record', 'About']
    # choice = st.sidebar.selectbox('Action', menu)
    # create_table()

    if tabs == 'Login':
        st.subheader('🧑‍💻️ Snowflake authorization')

        # with open('../config.yaml') as file:
        #     config = yaml.load(file, Loader=SafeLoader)

        # authenticator = stauth.Authenticate(
        #     config['credentials'],
        #     config['cookie']['name'],
        #     config['cookie']['key'],
        #     config['cookie']['expiry_days'],
        #     config['preauthorized']
        # )

        userid = st.text_input('Username').lower()
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            if userid == '' or password == '':
                st.warning('Please provide account and password to login.')
            else:
                st.success("You was successfully logged in.")

    elif tabs == 'Organization':
        st.subheader('Organization list')

        df = view_data_organization()
        df = pd.DataFrame(df,
                          columns=['ORG', 'PARENT', 'ORG_ID', 'LEVEL', 'NAME'])

        # df = df.set_index('ORG_ID')
        df_selected = st.multiselect("Select ORG_ID:", [str(i[0]) for i in view_all_org_ids()])  # set(df.index))
        df_selected = view_data_organization(df_selected)  # df.loc[df_selected]

        # if not df_selected.empty:
        #     st.dataframe(df_selected, use_container_width=True)
        # else:
        df_selected = pd.DataFrame(df_selected,
                                   columns=['ORG', 'PARENT', 'ORG_ID', 'LEVEL', 'NAME'])
        st.dataframe(df_selected,
                     use_container_width=True)

        st.subheader('Add new record')
        col1, col2 = st.columns(2)

        with col1:
            org = st.text_input('ORG')
            list_of_records = ['<NA>'] + [str(i[0]) for i in view_all_org_ids()]
            parent = st.selectbox('PARENT', list_of_records, index=0)
            if parent == '<NA>':
                org_id = st.text_input('ORG_ID', disabled=True, value=org.upper())
            else:
                org_id = st.text_input('ORG_ID', disabled=True, value=parent + "-" + org.upper())

        with col2:
            if parent == '<NA>':
                parent_level = [-1]
            else:
                parent_level = get_parent_level(parent)
            parent_level = pd.DataFrame(parent_level)
            level = st.text_input('LEVEL', int(parent_level[0].values + 1), disabled=True)
            name = st.text_input('NAME', 'Dummy name')

        if st.button('Submit'):
            df = view_all_org_ids()
            df = pd.DataFrame(df)

            if org_id in set(df.values[:, 0]):
                st.error("ORGANIZATION is already exists: ORG_ID = '{}' ".format(org_id))
            else:
                insert_organization(org.upper(), parent, org_id, int(level), name)
                st.success("New record added to ORGANIZATION: ORG_ID = '{}'".format(org_id))

    elif tabs == 'Funding Line':
        st.subheader('Funding Line list')

        df = view_data_funding_line()
        df = pd.DataFrame(df,
                          columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
        # st.info(index)

        col1, col2 = st.columns(2)
        with col1:
            df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
        with col2:
            df_name = st.multiselect("Select NAME:", set(df['NAME']))

        df_selected = view_data_funding_line(df_org, df_name)
        df_selected = pd.DataFrame(df_selected,
                                   columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
        st.dataframe(df_selected,
                     use_container_width=True)

        st.subheader('Add new record')
        col1, col2 = st.columns(2)

        with col1:
            last_row = get_last_row_funding_line()
            last_row = pd.DataFrame(last_row)
            # st.info(last_row[0].values)
            id = st.text_input('ID', int(last_row[0].values + 1), disabled=True)
            list_of_records = [i[0] for i in view_all_org_ids()]
            org_id = st.selectbox('ORG_ID', list_of_records)
            name = st.text_input('NAME', 'Dummy name')

        with col2:
            funding_type = st.text_input('FUNDING_TYPE', 'Dummy funding type')
            version = st.number_input('VERSION', 0)
            top_line = st.selectbox('TOP_LINE', ('FALSE', 'TRUE'))
            note = st.text_area('NOTE', 'Dummy note')

        if st.button('Submit'):
            df = exists_funding_line(org_id, name, version)
            df = pd.DataFrame(df)

            if not df.empty:
                st.error("FUNDING LINE is already exists: ORG_ID = '{}', NAME = '{}', VERSION = {} ".format(
                    org_id, name, version))
            else:
                insert_funding_line(int(last_row[0].values + 1), org_id, name, funding_type, version, top_line, note)
                st.success("New record added to FUNDING LINE: ORG_ID = '{}', NAME = '{}', VERSION = {}".format(
                    org_id, name, version))

    elif tabs == 'Edit Line':
        st.subheader('Edit Funding Line')

        df = view_data_funding_line()
        df = pd.DataFrame(df,
                          columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
        # st.dataframe(df,
        #              use_container_width=True)

        df_line_id = st.selectbox("Select ID:", set(df['ID']))
        df_selected = view_data_funding_line(None, None, df_line_id)
        df_selected = pd.DataFrame(df_selected,
                                   columns=['ID', 'ORG_ID', 'NAME', 'FUNDING_TYPE', 'VERSION', 'TOP_LINE', 'NOTE'])
        st.dataframe(df_selected, use_container_width=True)

        st.subheader('Edit record')
        col1, col2 = st.columns(2)

        with col1:
            id = st.text_input('ID', df_selected['ID'][0], disabled=True)
            list_of_records = [i[0] for i in view_all_org_ids()]

            # st.write(df_selected['ORG_ID'][0].index)

            org_id = st.selectbox('ORG_ID', list_of_records, index=0)
            name = st.text_input('NAME', df_selected['NAME'][0])

        with col2:
            funding_type = st.text_input('FUNDING_TYPE', df_selected['FUNDING_TYPE'][0])
            version = st.number_input('VERSION', df_selected['VERSION'][0])
            top_line = st.selectbox('TOP_LINE', ('FALSE', 'TRUE'), bool(df_selected['TOP_LINE'][0]))
            note = st.text_area('NOTE', df_selected['NOTE'][0])

        if st.button('Submit'):
            update_funding_line(id, org_id, name, funding_type, version, top_line, note)
            st.success("Existing FUNDING LINE record was updated: "
                       "ID = {}, ORG_ID = '{}', NAME = '{}', FUNDING_TYPE = '{}', VERSION = {}, TOP_LINE = {}, "
                       "NOTE = '{}' ".format(
                id, org_id, name, funding_type, version, top_line, note))

    elif tabs == 'Funding Amount':
        st.subheader('Funding Amount list')

        df = view_data_funding_amount()
        df = pd.DataFrame(df,
                          columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                   'SOURCE_URL',
                                   'NOTE', 'ORG_ID', 'NAME'])

        col1, col2 = st.columns(2)
        with col1:
            df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
            df_name = st.multiselect("Select NAME:", set(df['NAME']))
        with col2:
            df_year = st.multiselect("Select FISCAL_YEAR:", set(df['FISCAL_YEAR']))
            df_step = st.multiselect("Select STEP:", set(df['STEP']))

        df_selected = view_data_funding_amount(df_org, df_name, df_year, df_step)
        df_selected = pd.DataFrame(df_selected,
                                   columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                            'SOURCE_URL',
                                            'NOTE', 'ORG_ID', 'NAME'])
        st.dataframe(df_selected,
                     use_container_width=True)

        st.subheader('Add new record')
        col1, col2 = st.columns(2)

        with col1:
            list_of_records = [i[0] for i in view_all_funding_ids()]
            funding_line_id = st.selectbox('FUNDING_LINE_ID', list_of_records)
            fiscal_year = st.selectbox('FISCAL_YEAR', ('2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017',
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
                                                       '2098', '2099'))
            step = st.selectbox('STEP', ('Request', 'House', 'Senate', 'Enacted'))

        with col2:
            amount = st.number_input('AMOUNT')
            amount_type = st.text_input('AMOUNT_TYPE', 'Dummy amount type')
            source_url = st.text_input('SOURCE_URL', 'Dummy source url')
            note = st.text_area('NOTE', 'Dummy note')

        if st.button('Submit'):
            df = exists_funding_amount(funding_line_id, int(fiscal_year), step, amount_type)
            df = pd.DataFrame(df)

            if not df.empty:
                st.error("FUNDING AMOUNT is already exists: FUNDING_LINE_ID = '{}', FISCAL_YEAR = {}, STEP = '{}', "
                         "AMOUNT_TYPE = '{}' ".format(
                    funding_line_id, int(fiscal_year), step, amount_type))
            else:
                insert_funding_amount(funding_line_id, int(fiscal_year), step, amount, amount_type, source_url, note)
                st.success("New record added to FUNDING AMOUNT: "
                           "FUNDING_LINE_ID = '{}', "
                           "FISCAL_YEAR = {}, "
                           "STEP = '{}', "
                           "AMOUNT_TYPE = '{}'".format(
                    funding_line_id, fiscal_year, step, amount_type))

    elif tabs == 'Bulk download':
        st.subheader('Bulk download')

        df = view_data_funding_amount()
        df = pd.DataFrame(df,
                          columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                   'SOURCE_URL',
                                   'NOTE', 'ORG_ID', 'NAME'])

        col1, col2 = st.columns(2)
        with col1:
            df_org = st.multiselect("Select ORG_ID:", set(df['ORG_ID']))
            df_name = st.multiselect("Select NAME:", set(df['NAME']))
        with col2:
            df_year = st.multiselect("Select FISCAL_YEAR:", set(df['FISCAL_YEAR']))
            df_step = st.multiselect("Select STEP:", set(df['STEP']))

        df_selected = view_data_funding_amount(df_org, df_name, df_year, df_step)
        df_selected = pd.DataFrame(df_selected,
                                   columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                            'SOURCE_URL',
                                            'NOTE', 'ORG_ID', 'NAME'])
        st.dataframe(df_selected,
                     use_container_width=True)

        @st.experimental_memo
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(df_selected)

        st.download_button(
            "Press to Download",
            csv,
            "funding_amount.csv",
            "text/csv",
            key='download-csv'
        )
        st.success('The file successfully downloaded.')

    elif tabs == 'Bulk upload':
        st.subheader('Bulk upload')

        uploaded_file = st.file_uploader('Upload CSV', type='.csv')

        # use_example_file = st.checkbox('Use example file', False, help='Use in-built example file to demo the app')
        # If CSV is not uploaded and checkbox is filled, use values from the example file
        # and pass them down to the next if block
        # if use_example_file:
        #     uploaded_file = 'demo_file.csv'

        if uploaded_file:
            csv_df = pd.read_csv(uploaded_file,
                                 delimiter=';',
                                 header=None,
                                 names=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL',
                                        'NOTE', 'ORG_ID', 'NAME'],
                                 skiprows=1)

            with st.expander('File data preview'):
                csv_df = pd.DataFrame(csv_df,
                                      columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE',
                                               'SOURCE_URL', 'NOTE'])

                st.dataframe(csv_df)

            # type(uploaded_file) == str, means the example file was used
            # name = ('demo_file.csv' if isinstance(uploaded_file, str) else uploaded_file.name)

            # st.write('')
            # st.write('### Review existing records in the Snowflake database')
            # st.write('')

            # snow_df = get_record_list(csv_df['FUNDING_LINE_ID'])
            # snow_df = pd.DataFrame(snow_df,
            #                        columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL', 'NOTE'])

            st.write('')
            st.write('### Upload from ', uploaded_file.name)
            st.write('')

            if st.button('Submit'):

                if not csv_df.empty:
                    for row in csv_df.itertuples():
                        # st.info(row)
                        funding_line_id = row.FUNDING_LINE_ID
                        fiscal_year = row.FISCAL_YEAR
                        step = row.STEP
                        amount = row.AMOUNT
                        amount_type = row.AMOUNT_TYPE
                        source_url = row.SOURCE_URL
                        note = row.NOTE

                        df_amount = exists_funding_amount(funding_line_id, int(fiscal_year), step, amount_type)
                        df_amount = pd.DataFrame(df_amount)

                        if not df_amount.empty:
                            update_funding_amount(funding_line_id, int(fiscal_year), step, amount_type,
                                                  int(fiscal_year), step, amount,
                                                  amount_type, source_url, note)
                            st.warning("Existing FUNDING AMOUNT record was updated: "
                                       "FUNDING_LINE_ID = '{}', FISCAL_YEAR = {}, STEP = '{}', AMOUNT_TYPE = '{}' ".format(
                                funding_line_id, int(fiscal_year), step, amount_type))
                        else:
                            insert_funding_amount(funding_line_id, int(fiscal_year), step, amount, amount_type,
                                                  source_url, note)
                            st.success("New record added to FUNDING AMOUNT: "
                                       "FUNDING_LINE_ID = '{}', "
                                       "FISCAL_YEAR = {}, "
                                       "STEP = '{}', "
                                       "AMOUNT_TYPE = '{}'".format(
                                funding_line_id, fiscal_year, step, amount_type))

    elif tabs == 'Add/Edit':
        st.subheader('Add/Edit a record')

        df = view_data_funding_amount()
        df = pd.DataFrame(df, columns=['FUNDING_LINE_ID', 'FISCAL_YEAR', 'STEP', 'AMOUNT', 'AMOUNT_TYPE', 'SOURCE_URL',
                                       'NOTE'])

        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            list_of_records = [i[0] for i in view_all_funding_ids()]
            funding_line_id = st.selectbox('FUNDING_LINE_ID', list_of_records)
            fiscal_year = st.number_input('FISCAL_YEAR', format='%i')
            step = st.text_input('STEP')

        with col2:
            amount = st.number_input('AMOUNT')
            amount_type = st.text_input('AMOUNT_TYPE')
            source_url = st.text_input('SOURCE_URL')
            note = st.text_area('NOTE')

        if st.button('Submit'):
            insert_funding_amount(funding_line_id, fiscal_year, step, amount, amount_type, source_url, note)
            st.success("New record added to FUNDING AMOUNT: '{}'".format(
                str(funding_line_id) + " " + str(fiscal_year) + " " + step))

    else:
        st.subheader('About')
        st.info('Build for AIP.ORG by Dmitry Taranenko@dPrism')


if __name__ == '__main__':
    main()
