import pandas as pd
import aip
from aip import *

form = aip.build(page_title='Edit Line', page_icon='📝')
sf = aip.get_snowflake()

if sf.connected():
    with form:
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

        if st.form_submit_button('Submit'):
            sf.update_funding_line(id, org_id, name, funding_type, version, top_line, note)
            st.success("Existing FUNDING LINE record was updated: "
                       "ID = {}, ORG_ID = '{}', NAME = '{}', FUNDING_TYPE = '{}', VERSION = {}, TOP_LINE = {}, "
                       "NOTE = '{}' ".format(
                id, org_id, name, funding_type, version, top_line, note))
            st.experimental_rerun()