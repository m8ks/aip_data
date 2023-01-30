import snowflake.connector

connect = snowflake.connector.connect(
    user='DMITRYT', password='789321QWEqaz',
    account='xxb05879.us-east-1',
    database='AIP_TEST',
    schema='AIP',
    warehouse='AIP_WAREHOUSE_TEST',
    role='ACCOUNTADMIN',
    insecure_mode=True,
    # ocsp_fail_open=False,
    use_openssl_only=False)

cx = connect.cursor()


def insert_record(key, funding_line_id, fiscal_year, step, amount, notes):
    cx.execute(
        "INSERT INTO FUNDINGAMOUNTS(KEY, FUNDINGLINEID, FISCALYEAR, STEP, AMOUNT, NOTES2) VALUES ({}, '{}','{}','{}',{},'{}')".format(
            key, funding_line_id, fiscal_year, step, amount, notes))
    connect.commit()


def view_data():
    cx.execute('SELECT * FROM FUNDINGAMOUNTS')  # WHERE FUNDINGLINEID = \'DOE-OS\' AND FISCALYEAR = 2022')
    data = cx.fetchall()
    return data


def view_all_ids():
    cx.execute('SELECT DISTINCT KEY FROM FUNDINGAMOUNTS')
    data = cx.fetchall()
    return data


def get_last_id():
    cx.execute('SELECT MAX(KEY) FROM FUNDINGAMOUNTS')
    data = cx.fetchall()
    return data


def get_record(key):
    cx.execute(
        'SELECT KEY, FUNDINGLINEID, FISCALYEAR, STEP, AMOUNT, NOTES2 FROM FUNDINGAMOUNTS WHERE KEY ={}'.format(key))
    # FUNDINGLINEID ="{}" AND STEP ="{}" AND FISCALYEAR ="{}"'.format(funding_line_id, step, fiscal_year))
    data = cx.fetchall()
    return data


def get_record_list(key_list):
    for index, value in key_list.items():
        if index == 0:
            query_str = 'KEY = {}'.format(value)
        else:
            query_str += ' OR KEY = {}'.format(value)

    cx.execute(
        'SELECT KEY, FUNDINGLINEID, FISCALYEAR, STEP, AMOUNT, NOTES2 FROM FUNDINGAMOUNTS WHERE {}'.format(query_str))

    data = cx.fetchall()
    return data


def update_record(new_amount, new_notes, key):  # funding_line_id, step, fiscal_year):
    cx.execute("UPDATE FUNDINGAMOUNTS SET AMOUNT ={}, NOTES2='{}' WHERE KEY = {}".format(new_amount, new_notes,
                                                                                         key))  # FUNDINGLINEID='{}' and STEP='{}' and FISCALYEAR='{}' ".format(
    # new_amount, new_notes, funding_line_id, step, fiscal_year))
    connect.commit()
    data = cx.fetchall()
    return data


def update_record_list(key_list):
    for index, value in key_list['ID']:
        cx.execute("UPDATE FUNDINGAMOUNTS SET AMOUNT ={}, NOTES2='{}' WHERE KEY = {}".format(key_list['AMOUNT'], key_list['NOTES'],
                                                                                             key_list['ID']))
    connect.commit()
    data = cx.fetchall()
    return data

def delete_record(key):
    cx.execute('DELETE FROM FUNDINGAMOUNTS WHERE KEY ={}'.format(key))
    connect.commit()
