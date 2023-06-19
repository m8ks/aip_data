import streamlit as st
import pandas as pd
import aip

aip.build(page_title='Bulk upload', page_icon='📤', add_form=False)
sf = aip.get_snowflake()

if sf.connected():
    st.info('You can use bulk upload by selecting the csv file, \n'
            'please verify the data and push it into the Preview table by clicking \'Submit\' button')

    config = aip.get_yaml()

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
                    userid = sf.current_user()

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

                    st.success('Upload was successfully completed.')
                    st.experimental_rerun()

        except Exception as e:
            st.error(str(e))

