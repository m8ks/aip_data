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

cookie_name = 'streamlit_cookie'


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_manager():
    return stx.CookieManager()


cookie_manager = get_manager()
cookie_manager.get_all()

if cookie_manager.get(cookie_name):
    cookie_manager.delete(cookie_name)

# Title
st.title('Logout')
st.info('**You have successfully logged out. For login please click here: [Home page]('
        'https://aip-fyi-budget-tracker.streamlit.app)**', icon="🏠")
