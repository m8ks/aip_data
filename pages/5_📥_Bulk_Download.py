import streamlit as st
import pandas as pd
import aip

aip.build(page_title='Bulk download', page_icon='📥', add_form=False)
sf = aip.get_snowflake()

if sf.connected():
    st.info('How to download? \n'
            '- Filter items to download \n'
            '- Choose empty field option if you wnat to download with blank values \n'
            '- Verify that a csv file is downloaded to your computer '
            'with expected format and columns populated ')

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