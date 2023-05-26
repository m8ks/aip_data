import json
from json import JSONDecodeError
import streamlit as st
import pandas as pd

import re
from aip_db import *
import streamlit.components.v1 as stc
from st_on_hover_tabs import on_hover_tabs
from streamlit.runtime.runtime import Runtime, SessionInfo
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.web.server.server import Server
from datetime import datetime, timedelta
import base64
import extra_streamlit_components as stx

cookie_name = 'test_cookie'


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


def st_instance_of_type(type_obj: object) -> object:
    import gc
    st_obj = None
    for obj in gc.get_objects():
        if type(obj) is type_obj:
            st_obj = obj
            break
    return st_obj


def st_server_props():
    st_server = st_instance_of_type(Server)

    st_server_runtime = st_server._runtime
    st_gc_runtime = st_instance_of_type(Runtime)
    assert (st_server_runtime == st_gc_runtime)

    main_script_path = st_server.main_script_path
    browser_is_connected = st_server.browser_is_connected

    return {'st_server_runtime': st_server_runtime, 'st_gc_runtime': st_gc_runtime,
            'main_script_path': main_script_path, 'browser_is_connected': browser_is_connected}


def st_session_info() -> SessionInfo:
    st_runtime = st_instance_of_type(Runtime)
    # get session id from the current script runner thread
    session_id = add_script_run_ctx().streamlit_script_run_ctx.session_id
    # use the session id to retrieve the session info
    session_info = st_runtime._get_session_info(session_id)
    return session_info


def st_client_headers() -> dict:
    session_info = st_session_info()
    client_headers = session_info.client.request.headers._dict
    return dict(client_headers)


def st_client_cookies() -> dict:
    client_headers = st_client_headers()
    cookies_str = client_headers["Cookie"]
    results = re.findall(r"([\w]+)=([^;]+)", cookies_str)
    cookies = dict(results)
    return cookies


def save_cookie(userid, password, role="role1", schema="schema2", database="database3", account="account4", warehouse="warehouse5"):
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
    get_manager().set(cookie_name, base64_message, expires_at=datetime.max)


def get_cookie_values():
    user_value, password_value, role_value, expire_value, schema_value, database_value, account_value, warehouse_value \
        = None, None, None, None, None, None, None, None

    json_data = get_manager().get(cookie_name)

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

    return [user_value, password_value, role_value, expire_value, schema_value, database_value, account_value,
            warehouse_value]


def main():
    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)
    cookie_manager = get_manager()

    st.subheader("All Cookies:")

    st.write(get_manager().get_all())

    [user_value, password_value, role_value, expire_value, schema_value, database_value, account_value,
     warehouse_value] = get_cookie_values()

    st.write(user_value)

    c1, c2, c3 = st.columns(3)

    if user_value == '' or user_value is None:
        with c1:
            st.subheader("Get Cookie:")
            cookie = st.text_input("Cookie", key="0")
            clicked = st.button("Get")
            if clicked:
                value = cookie_manager.get(cookie=cookie)
                st.write(value)
        with c2:
            st.subheader("Set Cookie:")
            cookie = st.text_input("Cookie", key="1")
            val = st.text_input("Value")
            if st.button("Add"):
                save_cookie(cookie, val)
                # cookie_manager.set(cookie, val, expires_at=datetime.max)
        with c3:
            st.subheader("Delete Cookie:")
            cookie = st.text_input("Cookie", key="2")
            if st.button("Delete"):
                cookie_manager.delete(cookie)
    else:
        with st.sidebar:
            tabs = on_hover_tabs(
                tabName=['Home', 'Organization', 'Logout', 'About'],
                # iconName=['', '', '', '', '', '', '', '', ''],
                iconName=['home', 'table', 'logout'],
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
            st.info('Home')

        elif tabs == 'Organization':
            st.subheader('🏢 Organization list')
            st.info('Organization')

        elif tabs == 'Logout':
            cookie_manager.delete(cookie_name)

        else:
            st.subheader('About')
            st.info('Build for AIP.ORG by Dmitry Taranenko@dPrism')



if __name__ == '__main__':
    main()
