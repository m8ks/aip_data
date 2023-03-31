import snowflake.connector
import streamlit as st

connect = snowflake.connector.connect(
    user='CONTRACTORDMITRYT', password='789321QWEqaz',
    account='lib13297.us-east-1',
    database='FYI_BUDGET_TRACKER',
    schema='DEV',
    warehouse='FYI_COMPUTE_WH',
    role='ACCOUNTADMIN',
    insecure_mode=True,
    # ocsp_fail_open=False,
    use_openssl_only=False)

cx = connect.cursor()


# def insert_record(key, funding_line_id, fiscal_year, step, amount, notes):
#     cx.execute(
#         "INSERT INTO FUNDINGAMOUNTS(KEY, FUNDINGLINEID, FISCALYEAR, STEP, AMOUNT, NOTES2) VALUES ({}, '{}','{}','{}',{},'{}')".format(
#             key, funding_line_id, fiscal_year, step, amount, notes))
#     connect.commit()


def insert_organization(org, parent, org_id, level, name):
    if parent == '<NA>':
        cx.execute("INSERT INTO ORGANIZATION(ORG, ORG_ID, LEVEL, NAME) VALUES ('{}', '{}', {}, '{}')".format(
            org, org_id, level, name))
    else:
        cx.execute("INSERT INTO ORGANIZATION(ORG, PARENT, ORG_ID, LEVEL, NAME) VALUES ('{}', '{}', '{}', {}, '{}')".format(
                org, parent, org_id, level, name))
    connect.commit()


def view_data_organization(org_list=None):
    query_str = ''
    if org_list is None or org_list == []:
        cx.execute("SELECT * FROM ORGANIZATION ORDER BY ORG_ID")
    else:
        for index in org_list:
            if query_str is '':
                query_str = "ORG_ID = '{}' ".format(index)
            else:
                query_str += "OR ORG_ID = '{}' ".format(index)
        cx.execute("SELECT * FROM ORGANIZATION WHERE {} ORDER BY PARENT ASC".format(query_str))

    data = cx.fetchall()
    return data


def view_all_org_ids():
    cx.execute('SELECT DISTINCT ORG_ID FROM ORGANIZATION')
    data = cx.fetchall()
    return data


def get_parent_level(org):
    cx.execute("SELECT LEVEL FROM ORGANIZATION WHERE ORG_ID = '{}'".format(org))
    data = cx.fetchall()
    return data


def get_last_row():
    cx.execute('SELECT MAX(ORG) FROM ORGANIZATION')
    data = cx.fetchall()
    return data


def view_data_funding_line(df_org=None, df_name=None, df_id=None):
    query_org = ''
    query_name = ''

    if df_id:
        cx.execute("SELECT * FROM FUNDING_LINE WHERE ID = {} ORDER BY ID".format(df_id))
    else:
        if (df_org is None or df_org == []) and (df_name is None or df_name == []):
            cx.execute("SELECT * FROM FUNDING_LINE ORDER BY ID")
        else:
            if df_org:
                for index in df_org:
                    if query_org is '':
                        query_org = "ORG_ID = '{}' ".format(index)
                    else:
                        query_org += "OR ORG_ID = '{}' ".format(index)
                query_org = '(' + query_org + ')'
            else:
                query_org = '(1 = 1)'

            if df_name:
                for index in df_name:
                    if query_name is '':
                        query_name = "NAME = '{}' ".format(index)
                    else:
                        query_name += "OR NAME = '{}' ".format(index)
                query_name = '(' + query_name + ')'
            else:
                query_name = '(2 = 2)'

            cx.execute("SELECT * FROM FUNDING_LINE WHERE {} ORDER BY ID ASC".format(query_org + ' AND ' + query_name))

    data = cx.fetchall()
    return data


def get_last_row_funding_line():
    cx.execute('SELECT MAX(ID) FROM FUNDING_LINE')
    data = cx.fetchall()
    return data


def exists_funding_line(org_id, name, version):
    cx.execute(
        "SELECT ORG_ID, NAME, VERSION FROM FUNDING_LINE WHERE ORG_ID = '{}' AND NAME = '{}' AND VERSION = {}".format(
            org_id, name, version
        ))
    data = cx.fetchall()
    return data


def insert_funding_line(id, org_id, name, funding_type, version, top_line, note):
    cx.execute(
        "INSERT INTO FUNDING_LINE(ID, ORG_ID, NAME, FUNDING_TYPE, VERSION, TOP_LINE, NOTE) VALUES ({}, '{}', '{}', '{}', {}, {}, '{}')".format(
            id, org_id, name, funding_type, version, top_line, note))
    connect.commit()


def update_funding_line(id, org_id, name, funding_type, version, top_line, note):
    cx.execute(
        "UPDATE FUNDING_LINE SET "
        "ORG_ID = '{}', "
        "NAME = '{}', "
        "FUNDING_TYPE = '{}', "
        "VERSION = {},"
        "TOP_LINE = {}, "
        "NOTE = '{}' "
        "WHERE ID = {} ".format(
            org_id, name, funding_type, version, top_line, note, id))
    connect.commit()
    data = cx.fetchall()
    return data


def view_all_funding_ids():
    cx.execute("SELECT DISTINCT ID FROM FUNDING_LINE ORDER BY ID")
    data = cx.fetchall()
    return data


def view_data_funding_amount(df_org=None, df_name=None, df_year=None, df_step=None):
    query_org = ''
    query_name = ''
    query_year = ''
    query_step = ''

    if (df_org is None or df_org == []) and (df_name is None or df_name == []) and (
            df_year is None or df_year == []) and (df_step is None or df_step == []):
        cx.execute('SELECT '
                   'FA.FUNDING_LINE_ID, '
                   'FA.FISCAL_YEAR, '
                   'FA.STEP, '
                   'FA.AMOUNT, '
                   'FA.AMOUNT_TYPE, '
                   'FA.SOURCE_URL, '
                   'FA.NOTE ,'
                   'FL.ORG_ID ,'
                   'FL.NAME '
                   'FROM FUNDING_AMOUNT AS FA '
                   'JOIN FUNDING_LINE AS FL ON FA.FUNDING_LINE_ID = FL.ID '
                   'JOIN ORGANIZATION AS ORG ON FL.ORG_ID = ORG.ORG_ID ')
    else:
        if df_org:
            for index in df_org:
                if query_org is '':
                    query_org = "FL.ORG_ID = '{}' ".format(index)
                else:
                    query_org += "OR FL.ORG_ID = '{}' ".format(index)
            query_org = '(' + query_org + ')'
        else:
            query_org = '(1 = 1)'

        if df_name:
            for index in df_name:
                if query_name is '':
                    query_name = "FL.NAME = '{}' ".format(index)
                else:
                    query_name += "OR FL.NAME = '{}' ".format(index)
            query_name = '(' + query_name + ')'
        else:
            query_name = '(2 = 2)'

        if df_year:
            for index in df_year:
                if query_year is '':
                    query_year = "FA.FISCAL_YEAR = {} ".format(index)
                else:
                    query_year += "OR FA.FISCAL_YEAR = {} ".format(index)
            query_year = '(' + query_year + ')'
        else:
            query_year = '(3 = 3)'

        if df_step:
            for index in df_step:
                if query_step is '':
                    query_step = "FA.STEP = '{}' ".format(index)
                else:
                    query_step += "OR FA.STEP = '{}' ".format(index)
            query_step = '(' + query_step + ')'
        else:
            query_step = '(4 = 4)'

        cx.execute('SELECT '
                   'FA.FUNDING_LINE_ID, '
                   'FA.FISCAL_YEAR, '
                   'FA.STEP, '
                   'FA.AMOUNT, '
                   'FA.AMOUNT_TYPE, '
                   'FA.SOURCE_URL, '
                   'FA.NOTE ,'
                   'FL.ORG_ID ,'
                   'FL.NAME '
                   'FROM FUNDING_AMOUNT AS FA '
                   'JOIN FUNDING_LINE AS FL ON FA.FUNDING_LINE_ID = FL.ID '
                   'JOIN ORGANIZATION AS ORG ON FL.ORG_ID = ORG.ORG_ID '
                   'WHERE {}'.format(query_org + ' AND ' + query_name + ' AND ' + query_year + ' AND ' + query_step))

    data = cx.fetchall()
    return data


def exists_funding_amount(funding_line_id, fiscal_year, step, amount_type):
    cx.execute("SELECT * FROM FUNDING_AMOUNT "
               "WHERE FUNDING_LINE_ID = '{}' "
               "AND FISCAL_YEAR = {} "
               "AND STEP = '{}' "
               "AND AMOUNT_TYPE = '{}'".format(
                funding_line_id, fiscal_year, step, amount_type))
    data = cx.fetchall()
    return data


def insert_funding_amount(funding_line_id, fiscal_year, step, amount, amount_type, source_url, note):
    cx.execute(
        "INSERT INTO FUNDING_AMOUNT(FUNDING_LINE_ID, FISCAL_YEAR, STEP, AMOUNT, AMOUNT_TYPE, SOURCE_URL, NOTE) "
        "VALUES ({}, {}, '{}', {}, '{}', '{}', '{}')".format(
            funding_line_id, fiscal_year, step, amount, amount_type, source_url, note))
    connect.commit()


def update_funding_amount(funding_line_id, fiscal_year, step, amount_type, new_fiscal_year, new_step, new_amount,
                          new_amount_type, new_source_url, new_note):
    cx.execute(
        "UPDATE FUNDING_AMOUNT SET "
        "FISCAL_YEAR = {}, "
        "STEP = '{}', "
        "AMOUNT = {}, "
        "AMOUNT_TYPE = '{}',"
        "SOURCE_URL = '{}', "
        "NOTE = '{}' "
        "WHERE FUNDING_LINE_ID = '{}' "
        "AND FISCAL_YEAR = {} "
        "AND STEP = '{}' "
        "AND AMOUNT_TYPE = '{}'".format(
            new_fiscal_year, new_step, new_amount, new_amount_type, new_source_url, new_note,
            funding_line_id, fiscal_year, step, amount_type))
    connect.commit()
    data = cx.fetchall()
    return data


def get_funding_amount(funding_line_id):
    cx.execute(
        'SELECT * FROM FUNDING_AMOUNT WHERE FUNDING_LINE_ID ={}'.format(funding_line_id))
    data = cx.fetchall()
    return data


def get_funding_amount_list(funding_line_list):
    for index, value in funding_line_list.items():
        if index == 0:
            query_str = 'FUNDING_LINE_ID = {}'.format(value)
        else:
            query_str += ' OR FUNDING_LINE_ID = {}'.format(value)

    cx.execute(
        'SELECT * FROM FUNDING_AMOUNT WHERE {}'.format(query_str))

    data = cx.fetchall()
    return data


def update_funding_amount_list(funding_amount_list):
    for index, value in funding_amount_list['ID']:
        cx.execute("UPDATE FUNDINGAMOUNTS SET AMOUNT={}, NOTE='{}' WHERE FUNDING_LINE_ID = {}".format(
            funding_amount_list['AMOUNT'],
            funding_amount_list['NOTE'],
            funding_amount_list['FUNDING_LINE_ID']))
    connect.commit()
    data = cx.fetchall()
    return data


def delete_record(key):
    cx.execute('DELETE FROM FUNDINGAMOUNTS WHERE KEY ={}'.format(key))
    connect.commit()
