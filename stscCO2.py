# Program to calculate quantities relevent to LCA assessment of cooling methods
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt

import streamlit as st
import plotly.express as px
import pandas as pd

#########################################################################
# Experimental correlation: CO2 flow rate (kg/hr) vs nozzle diameter (mm)
#########################################################################
def scco2_CO2_flow_rate(d):
    CO2fr = 132.66*(d**1.7057)   # CO2 flow rate kg/hr
    return CO2fr

############################
# scCO2 system parameters
############################

# Set problem parameters and create parameters dictionary
# create problem parameters dictionary
def set_params():
    
    # assume each kg CO2 emitted during machining = 1 kg CO2 equivalent emissions
    st.session_state.scco2_CEfactor = 1.0
    st.session_state.scco2_flow_rate = 33.98   # kg/hr
    st.session_state.CI_elec = 0.149   # kg/kWh

    # production parameters
    st.session_state.machhrs_per_yr = 2000.0    # hours/year
    st.session_state.scco2_elec_pump_power = 0.311   # kW
    
    return

# end set_params

def scco2_calcs():

    # set problem parameters    
    scco2_CEfactor = st.session_state.scco2_CEfactor
    CI_elec = st.session_state.CI_elec

    # production parameters
    machhrs_per_yr = st.session_state.machhrs_per_yr
    scco2_elec_pump_power = st.session_state.scco2_elec_pump_power

    #########
    # CElecs
    #########
    scco2_elec_per_yr = machhrs_per_yr*scco2_elec_pump_power
    st.session_state.CE_elecs = scco2_elec_per_yr*CI_elec
    
    ######
    # CEc
    ######
    scco2_flow_rate = st.session_state.scco2_flow_rate    # kg/hr
    scco2_CEfactor = st.session_state.scco2_CEfactor
    scco2_per_yr = scco2_flow_rate*machhrs_per_yr    # kg/yr
    st.session_state.CE_c = scco2_per_yr*scco2_CEfactor
    
    # total CE emissions
    st.session_state.CE_mec = st.session_state.CE_elecs + st.session_state.CE_c
    
    return

# end emulsion_calcs

def plot_scco2_matplotlib_barchart():
    
    CE_elecs = st.session_state.CE_elecs
    CE_c = st.session_state.CE_c
    CE_mec = st.session_state.CE_mec
    species = (
        "CE emissions (kg) from scco2 cooling",
    )
    weight_counts = {
        "Electricity": np.array([CE_elecs,0]),
        "Nozzle CO2": np.array([CE_c,0]),
    }
    width = 0.2

    fig, ax = plt.subplots(figsize=(4,5))
    bottom = np.zeros(2)

    for boolean, weight_count in weight_counts.items():
        p = ax.bar(species, weight_count, width, label=boolean, bottom=bottom)
        bottom += weight_count
    ax.set_title("CE emissions (kg) from scCO2 cooling")
    ax.legend(loc="center")
    ax.set_ylabel('CE emissions (jg)')

    st.pyplot(plt)

# end plot_scco2_matplotlib_barchart

# Create barchart in plotly
def plot_scco2_plotly_barchart():

    # Need to create a pandas dataframce for use within plotly
    CE_elecs = st.session_state.CE_elecs
    CE_c = st.session_state.CE_c
    dfCE = pd.DataFrame({'scco2 cooling': [""], 'CE_elecs': CE_elecs, 'CE_c': CE_c})

    fig = px.bar(dfCE, x='scco2 cooling', y=["CE_elecs", "CE_c"],
                 labels={
                     "scco2 cooling": "scco2 cooling",
                     "y": "CEeq (kg)"},
                 title='CEeq (kg): emissions from scco2 cooling')
    fig.update_yaxes(title='CEeq (kg)')
    st.plotly_chart(fig)

# end plot_scco2_plotly_barchart

# Main program
st.title("SccO2 Cooling CO2 Modelling Program")
st.write("This application enables you to calculate the CO2 eq kg cost of scCO2 cooling")
st.write("Click the 'CO2 bar chart' tab to display CO2 eq kg bar chart")
st.markdown("---")

set_params()
scco2_calcs()
tab1, tab2 = st.tabs(["CO2eq (kg) calculator", "CO2eq (kg) bar chart"])

# CO2 eq kg calculator tab
with tab1:

    # Create the input - Row 1
    row1 = st.columns([1,1,1])

    #  CI elec (kg/kWh)
    default_value = 0.149
    st.session_state.CI_elec = default_value
    CI_elec = row1[0].number_input("CI elec (kg/kWh)", 0.1, 0.2, default_value)
    st.session_state.CI_elec = CI_elec

    #  Machining hours per year
    default_value = 2000.0
    st.session_state.machhrs_per_yr = default_value
    machhrs_per_yr = row1[1].number_input("Machining hours per year", 1800.0, 2200.0, default_value)
    st.session_state.machhrs_per_yr = machhrs_per_yr

    #  Electrical pumping power (kW)
    default_value = 0.311
    st.session_state.scco2_elec_pump_power = default_value
    scco2_elec_pump_power = row1[2].number_input("Electrical pumping power (kW)", 0.1, 0.5, default_value)
    st.session_state.scco2_elec_pump_power = scco2_elec_pump_power

    # Create the inputs - Row 2
    row2 = st.columns([1,1,1])

    #  scco2 CE conversion factor
    default_value = 1.0
    st.session_state.scco2_CEfactor = default_value
    scco2_CEfactor = row2[0].number_input("scCO2 cCE conversion factor", 0.2, 5.0, default_value)
    st.session_state.scco2_CEfactor = scco2_CEfactor
    
    #  Nozzle diameter - used to scCO2 flow rate (kg/hr)
    default_value = 0.15
    st.session_state.d_nozzle = default_value
    d_nozzle = row2[1].number_input("Nozzle diameter (mm)", 0.1, 0.5, default_value)
    st.session_state.d_nozzle = d_nozzle
    st.session_state.scco2_flow_rate = scco2_CO2_flow_rate(d_nozzle)

    st.write("Calculated scCO2 flow rate (kg/hr)",st.session_state.scco2_flow_rate)
    st.markdown("---")
    scco2_calcs()
    st.write("Total scCO2 CO2eq (kg)",st.session_state.CE_mec)

# Cost bar chart tab
with tab2:
    plot_scco2_plotly_barchart()


