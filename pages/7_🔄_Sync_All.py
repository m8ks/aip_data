import streamlit as st
import pandas as pd
import aip

form = aip.build(page_title='Review and push into Snowflake', page_icon='🔄️')
sf = aip.get_snowflake()

if sf.connected():
    with form:
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

        if st.form_submit_button('Submit'):

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

                userid = sf.current_user()

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

        if st.form_submit_button('Clear'):
            if select_org == [] and select_name == [] and select_year == [] and select_step == []:
                st.warning('All items from Preview table will be purged.. please wait')

            for row in df_selected.itertuples():
                sf.delete_funding_amount_upload(userid, row.FUNDING_LINE_ID, row.FISCAL_YEAR, row.STEP, row.AMOUNT_TYPE)

            st.success('Purge was successfully completed.')
            st.experimental_rerun()