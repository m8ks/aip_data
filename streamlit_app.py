import streamlit as st
import pandas as pd
from aip_db import *
import streamlit.components.v1 as stc
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode

# from snowflake.snowpark import Session
# import json
# from snowflake.snowpark.functions import col, call_builtin

HTML_BANNER = ("    \n"
               "    <div style=\"background-color:#0B074E;padding:10px;border-radius:10px\">\n"
               "    <img src=\"https://www.aip.org/sites/default/files/aip-logo-180.png\">\n"
               "    <h1 style=\"color:white;text-align:center;\">Datа management demo</h1>\n"
               "    <p style=\"color:white;text-align:center;\">Built with Streamlit</p>\n"
               "    </div>\n"
               "    ")


def main():
    stc.html(HTML_BANNER)

    choice2 = st.sidebar.selectbox('Table name',
                                   ['AGENCYINFO', 'CHANGEOVERPRIORYEAR', 'CHARTLABELS', 'FUNDINGAMOUNTS', 'PRIORYEAR', 'WEBTABLEROWLABELS'],
                                   index=3)

    menu = ['Bulk upload', 'Bulk update', 'Bulk delete', 'View all', 'Create record', 'Update record', 'About']
    choice = st.sidebar.selectbox('Action', menu)
    # create_table()

    if choice == 'Bulk upload':
        st.subheader('Bulk upload')

        uploaded_file = st.file_uploader('Upload CSV', type='.csv')

        use_example_file = st.checkbox(
            'Use example file', False, help='Use in-built example file to demo the app'
        )

        # If CSV is not uploaded and checkbox is filled, use values from the example file
        # and pass them down to the next if block
        if use_example_file:
            uploaded_file = 'demo_file.csv'

        if uploaded_file:
            columns = ['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES']
            csv_df = pd.read_csv(uploaded_file,
                                 delimiter=';',
                                 header=None,
                                 names=columns,
                                 skiprows=1)

            with st.expander('File data preview'):
                # st.dataframe(csv_df.head(9999))
                # st.write('')
                # st.info(len(df))
                csv_df = pd.DataFrame(csv_df,
                                      columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES'])

                gb = GridOptionsBuilder.from_dataframe(csv_df)
                gb.configure_pagination()
                # gb.configure_side_bar()
                gb.configure_default_column(editable=False)

                grid_options = gb.build()

                csv_ag = AgGrid(csv_df,
                                gridOptions=grid_options,
                                enable_enterprise_modules=True,
                                fit_columns_on_grid_load=True,
                                allow_unsafe_jscode=True,
                                reload_data=False,
                                height=200)

            # type(uploaded_file) == str, means the example file was used
            name = (
                'demo_file.csv' if isinstance(uploaded_file, str) else uploaded_file.name
            )

            st.write('')
            st.write('### Review existing records in the Snowflake database')
            st.write('')

            snow_df = get_record_list(csv_df['ID'])
            snow_df = pd.DataFrame(snow_df,
                                   columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES'])

            gb = GridOptionsBuilder.from_dataframe(snow_df)

            gb.configure_pagination()
            gb.configure_side_bar()
            gb.configure_selection(header_checkbox=True, selection_mode="multiple", use_checkbox=True)
            gb.configure_default_column(editable=False)
            gb.configure_column('AMOUNT', cellStyle={'color': 'red'})
            gb.configure_column('Action',
                                cellEditor='agRichSelectCellEditor',
                                cellEditorParams={'values': ['Update', 'Skip']},
                                cellEditorPopup=True)

            grid_options = gb.build()

            js = JsCode("""
                            function(e) {
                                let api = e.api;
                                let rowIndex = e.rowIndex;
                                let col = e.column.colId;

                                let rowNode = api.getDisplayedRowAtIndex(rowIndex);
                                api.flashCells({
                                  rowNodes: [rowNode],
                                  columns: [col],
                                  flashDelay: 10000000000
                                });

                            };
                            """)

            gb.configure_grid_options(onCellValueChanged=js)

            snow_ag = AgGrid(snow_df,
                             gridOptions=grid_options,
                             enable_enterprise_modules=True,
                             fit_columns_on_grid_load=True,
                             allow_unsafe_jscode=True,
                             reload_data=False,
                             height=200)

            st.write('')
            st.write('### Bulk upload from ', name)
            st.write('')

            if st.button('Submit'):

                selected = snow_ag['selected_rows']
                selected_df = pd.DataFrame(selected)

                # selected_indices = [i['_selectedRowNodeInfo']
                #                     ['nodeRowIndex'] for i in selected]
                # st.info(selected_indices)

                if not csv_df.empty:
                    for row in csv_df.itertuples():
                        # st.info(row)

                        key = row.ID
                        funding_line_id = row.FUNDINGLINEID
                        fiscal_year = row.FISCALYEAR
                        step = row.STEP
                        amount = row.AMOUNT
                        notes = row.NOTES

                        # if selected:
                            # st.info(row[1])
                            # st.info(selected_df['ID'].values[0])
                            # st.info(csv_ag['data'][snow_df['ID'] == key])

                        if selected and row.ID in selected_df['ID'].values:
                            update_record(amount, notes, key)
                            st.warning("Updated: {} {} {} {} {} {}.".format(
                                key, funding_line_id, fiscal_year, step, amount, notes))

                        elif row.ID in snow_df['ID'].values:
                            st.error("Skipped: {} {} {} {} {} {}.".format(
                                key, funding_line_id, fiscal_year, step,
                                snow_ag['data'][snow_df['ID'] == key].values[0][4],
                                snow_ag['data'][snow_df['ID'] == key].values[0][5]))

                        else:
                            insert_record(key, funding_line_id, fiscal_year, step, amount, notes)
                            st.success("Inserted: {}, {}, {}, {}, {}, {}.".format(
                                key, funding_line_id, fiscal_year, step, amount, notes))

    elif choice == 'Bulk update':
        st.subheader('Bulk update')

        df = view_data()
        df = pd.DataFrame(df,
                          columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES'])

        gb = GridOptionsBuilder.from_dataframe(df)

        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(editable=False)
        gb.configure_selection(header_checkbox=True, selection_mode="multiple", use_checkbox=True)
        gb.configure_column('AMOUNT', editable=True)
        gb.configure_column('NOTES', editable=True)

        grid_options = gb.build()

        js = JsCode("""
                        function(e) {
                            let api = e.api;
                            let rowIndex = e.rowIndex;
                            let col = e.column.colId;

                            let rowNode = api.getDisplayedRowAtIndex(rowIndex);
                            api.flashCells({
                              rowNodes: [rowNode],
                              columns: [col],
                              flashDelay: 10000000000
                            });

                        };
                        """)

        gb.configure_grid_options(onCellValueChanged=js)

        ag = AgGrid(df,
                    gridOptions=grid_options,
                    enable_enterprise_modules=True,
                    fit_columns_on_grid_load=True,
                    allow_unsafe_jscode=True,
                    reload_data=False,
                    height=400)

        if st.button('Update'):
            selected = ag['selected_rows']
            selected_df = pd.DataFrame(selected, columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT',
                                                          'NOTES'])  # .apply(pd.to_numeric, errors='coerce')

            if not selected_df.empty:
                for row in selected_df.itertuples():
                    key = row.ID
                    funding_line_id = row.FUNDINGLINEID
                    fiscal_year = row.FISCALYEAR
                    step = row.STEP
                    amount = row.AMOUNT
                    notes = row.NOTES
                    update_record(amount, notes, key)
                    st.success("Updated: {}, {}, {}, {}, {}, {}.".format(
                        key, funding_line_id, fiscal_year, step, amount, notes))

                # st.subheader("Returned Data")
                # st.dataframe(selected_df)

            else:
                st.warning('Please select at least one record for update')

    elif choice == 'Create record':
        st.subheader('Create record')
        col1, col2 = st.columns(2)

        with col1:
            note = st.text_area('Funding amounts note')

        with col2:
            key = st.number_input('Key', get_last_id()[0][0])
            funding_line_id = st.text_input('Funding Line ID', 'DOE-OS')
            fiscal_year = st.number_input('Fiscal Year', 2024)
            step = st.selectbox('Step', ['Enacted', 'Actual', 'Request',
                                         'Request Plus Mandatory', 'House', 'Senate', 'Request w Add',
                                         'House Stimulus'])
            amount = st.number_input('Amount')

        if st.button('Submit'):
            insert_record(key, funding_line_id, fiscal_year, step, amount, note)
            st.success("Added: {}, {}, {}, {}, {}, {}.".format(key, funding_line_id, fiscal_year, step, amount, note))

    elif choice == 'View all':
        st.subheader('View all records')
        result = view_data()
        df = pd.DataFrame(result,
                          columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES'])

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(editable=False)

        grid_options = gb.build()

        ag = AgGrid(df,
                    height=400,
                    gridOptions=grid_options,
                    enable_enterprise_modules=True,
                    fit_columns_on_grid_load=True)

    elif choice == 'Update record':
        st.subheader('Update record')
        with st.expander('Current record'):
            result = view_data()
            clean_df = pd.DataFrame(result,
                                    columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES'])
            st.dataframe(clean_df)

        list_of_records = [i[0] for i in view_all_ids()]
        selected_id = st.selectbox('KEY', list_of_records)
        return_id = get_record(selected_id)

        if return_id:
            key = return_id[0][0]
            # funding_line_id = return_id[0][1]
            # fiscal_year = return_id[0][2]
            # step = return_id[0][3]
            amount = return_id[0][4]
            notes = return_id[0][5]

            col1, col2 = st.columns(2)

            with col1:
                new_note = st.text_area('New note', notes)

            with col2:
                # new_step = st.selectbox(step, ["Enacted", "Actual", "Request",
                #                                "Request Plus Mandatory", "House", "Senate", "Request w Add",
                #                                "House Stimulus"])
                new_amount = st.number_input('New amount', amount)

            if st.button('Update record'):
                update_record(new_amount, new_note, key)  # funding_line_id, fiscal_year, step)
                st.success("Updated: {}, '{}'".format(new_amount, new_note))

            with st.expander('View updated record'):
                result = get_record(key)
                clean_df = pd.DataFrame(result,
                                        columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES'])
                st.dataframe(clean_df)

    elif choice == 'Bulk delete':
        st.subheader('Delete record')
        df = pd.DataFrame(view_data(),
                          columns=['ID', 'FUNDINGLINEID', 'FISCALYEAR', 'STEP', 'AMOUNT', 'NOTES'])

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_side_bar()
        gb.configure_default_column(editable=False)
        gb.configure_selection(header_checkbox=True, selection_mode="multiple", use_checkbox=True)

        grid_options = gb.build()

        ag = AgGrid(df,
                    gridOptions=grid_options,
                    enable_enterprise_modules=True,
                    fit_columns_on_grid_load=True,
                    height=400)

        if st.button('Delete'):
            selected = ag['selected_rows']
            selected_df = pd.DataFrame(selected)

            if not selected_df.empty:
                for row in selected_df.itertuples():
                    key = row.ID
                    funding_line_id = row.FUNDINGLINEID
                    fiscal_year = row.FISCALYEAR
                    step = row.STEP
                    amount = row.AMOUNT
                    notes = row.NOTES
                    delete_record(key)
                    st.success(
                        "Deleted: {}, {}, {}, {}, {}, {}.".format(key, funding_line_id, fiscal_year, step, amount,
                                                                  notes))
            else:
                st.warning('Please select at least one record for delete')

    else:
        st.subheader('About')
        st.info('Build for AIP.ORG by Dmitry Taranenko@dPrism')


if __name__ == '__main__':
    main()
