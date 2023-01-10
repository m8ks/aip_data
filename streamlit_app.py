import streamlit as st
import pandas as pd
from aip_db import *
import streamlit.components.v1 as stc

HTML_BANNER = ("\n"
               "    <div style=\"background-color:#464e5f;padding:10px;border-radius:10px\">\n"
               "    <h1 style=\"color:white;text-align:center;\">AIP.ORG datа management demo</h1>\n"
               "    <p style=\"color:white;text-align:center;\">Built with Streamlit</p>\n"
               "    </div>\n"
               "    ")


def main():
    stc.html(HTML_BANNER)

    menu = ['Create', 'Read', 'Update', 'Delete', 'About']
    choice = st.sidebar.selectbox('Menu', menu)
    # create_table()

    if choice == 'Create':
        st.subheader('Add record')
        col1, col2 = st.columns(2)

        with col1:
            note = st.text_area('Funding amounts note')

        with col2:
            key = st.number_input('Key', 55555)
            funding_line_id = st.text_input('Funding Line ID', 'DOE-OS')
            fiscal_year = st.number_input('Fiscal Year', 2015)
            step = st.selectbox('Step', ['Enacted', 'Actual', 'Request',
                                         'Request Plus Mandatory', 'House', 'Senate', 'Request w Add',
                                         'House Stimulus'])
            amount = st.number_input('Amount', 7777)

        if st.button('Submit'):
            insert_record(key, funding_line_id, fiscal_year, step, amount, note)
            st.success('Added ::{} ::to FUNDINGAMOUNTS table'.format(funding_line_id))


    elif choice == 'Read':
        st.subheader('View records')
        with st.expander('View all records'):
            result = view_data()
            st.write(result)
            clean_df = pd.DataFrame(result, columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'UNDEFINED'])
            st.dataframe(clean_df)

        # with st.expander("STEP"):
        #    task_df = clean_df['STEP'].value_counts().to_frame()
        #    # st.dataframe(task_df)
        #    task_df = task_df.reset_index()
        #    st.dataframe(task_df)

        #    p1 = px.pie(task_df, names='index', values='STEP')
        #    st.plotly_chart(p1, use_container_width=True)


    elif choice == 'Update':
        st.subheader('Update record')
        with st.expander('Current record'):
            result = view_data()
            # st.write(result)
            clean_df = pd.DataFrame(result, columns=['FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT'])
            st.dataframe(clean_df)

        list_of_records = [i[0] for i in view_all_ids()]
        selected_id = st.selectbox('Key', list_of_records)
        return_id = get_record(selected_id)
        # st.write(task_result)

        if return_id:
            key = return_id[0][0]
            funding_line_id = return_id[0][1]
            fiscal_year = return_id[0][2]
            step = return_id[0][3]
            amount = return_id[0][4]
            notes = return_id[0][5]

            col1, col2 = st.columns(2)

            with col1:
                new_note = st.text_area('New note', notes)

            with col2:
                # new_step = st.selectbox(step, ["Enacted", "Actual", "Request",
                #                                "Request Plus Mandatory", "House", "Senate", "Request w Add",
                #                                "House Stimulus"])
                new_amount = st.number_input(amount)

            if st.button('Update record'):
                update_record(new_amount, new_note, funding_line_id, fiscal_year, step)
                st.success('Updated ::{} ::to FUNDINGAMOUNTS table {}'.format(amount, new_amount))

            with st.expander('View updated record'):
                result = view_data()
                # st.write(result)
                clean_df = pd.DataFrame(result, columns=['FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT'])
                st.dataframe(clean_df)


    elif choice == 'Delete':
        st.subheader('Delete record')
        with st.expander('View data'):
            result = view_data()
            # st.write(result)
            clean_df = pd.DataFrame(result, columns=['FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT'])
            st.dataframe(clean_df)

        unique_list = [i[0] for i in view_all_ids()]
        delete_by_id = st.selectbox('Select record', unique_list)
        if st.button('Delete'):
            delete_record(delete_by_id)
            st.warning('Deleted: \'{}\''.format(delete_by_id))

        with st.expander('Updated record'):
            result = view_data()
            # st.write(result)
            clean_df = pd.DataFrame(result, columns=['FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT'])
            st.dataframe(clean_df)

    else:
        st.subheader('About')
        st.info('Build for AIP.ORG by dPrism')
        #st.text('Dmitry Taranenko')


if __name__ == '__main__':
    main()
