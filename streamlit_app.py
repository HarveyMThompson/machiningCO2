# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 12:00:05 2024

@author: harveythompson
"""

import streamlit as st

flooded_page = st.Page("stemulsion.py", title="Emulsion cooling")
scco2_page = st.Page("stscCO2.py",title="ScCO2 + MQL cooling")

pg = st.navigation([flooded_page, scco2_page])
pg.run()