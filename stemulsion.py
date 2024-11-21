# Program to calculate quantities relevent to LCA assessment of cooling methods
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt

import streamlit as st
import plotly.express as px
import pandas as pd

############################
# Emulsion system parameters
############################
# High emulsion case
# Assume MWF makes is 75% oil/25% water

# Set problem parameters and create parameters dictionary
# create problem parameters dictionary
def set_params():
    
    params = dict()
    params['water_CEfactor'] = 0.000153    # kg/litre
    st.session_state.water_CEfactor = params['water_CEfactor']
    params['mwf_CEfactor'] = 1.2   # kg/litre
    st.session_state.mwf_CEfactor = params['mwf_CEfactor']
    params['emulsion_disposal_CEfactor'] = 0.2   # kg/litre
    st.session_state.emulsion_disposal_CEfactor = params['emulsion_disposal_CEfactor']
    params['CI_elec'] = 0.149   # kg/kWh
    st.session_state.CI_elec = params['CI_elec']

    # production parameters
    params['machhrs_per_yr'] = 2000.0    # hours/year
    st.session_state.machhrs_per_yr = params['machhrs_per_yr']
    params['elec_pump_power'] = 30.0   # kW
    st.session_state.elec_pump_power = params['elec_pump_power']

    # Medium emulsion case
    params['water_per_yr'] = 10560.0   # litres
    st.session_state.water_per_yr = params['water_per_yr']
    params['mwf_per_yr'] = 1080.0   # litres
    st.session_state.mwf_per_yr = params['mwf_per_yr']
    params['sumpchanges_per_yr'] = 4.0
    st.session_state.sumpchanges_per_yr = params['sumpchanges_per_yr']
    params['sump_vol'] = 3000.0    # litres
    st.session_state.sump_vol = params['sump_vol']

    # Water end of life evaporation calculations
    # In reality only applying the emulsion_disposal_CEfactor to entire emulsion
    params['T_initial'] = 20.0    # oC
    st.session_state.T_initial = params['T_initial']
    params['T_final'] =  100.0   # oC
    st.session_state.T_final = params['T_final']
    params['shcp_water'] = 4.19   # kJ/(litre.K)
    st.session_state.shcp_water = params['shcp_water']
    params['LH_water'] = 2260.0   # kJ/litre
    st.session_state.LH_water = params['LH_water']
    
    return params

# end set_params

def emulsion_calcs():

    # set problem parameters    
    water_CEfactor = st.session_state.water_CEfactor
    mwf_CEfactor = st.session_state.mwf_CEfactor
    emulsion_disposal_CEfactor = st.session_state.emulsion_disposal_CEfactor
    CI_elec = st.session_state.CI_elec

    # production parameters
    machhrs_per_yr = st.session_state.machhrs_per_yr
    elec_pump_power = st.session_state.elec_pump_power

    # Low emulsion case
    water_per_yr = st.session_state.water_per_yr
    mwf_per_yr = st.session_state.mwf_per_yr
    sumpchanges_per_yr = st.session_state.sumpchanges_per_yr
    sump_vol = st.session_state.sump_vol

    # Water end of life evaporation calculations
    # In reality only applying the emulsion_disposal_CEfactor to entire emulsionT_initial = 20.0    # oC
    T_initial = st.session_state.T_initial
    T_final = st.session_state.T_final
    shcp_water = st.session_state.shcp_water
    LH_water = st.session_state.LH_water

    #########################################################################
    # Emulsion Cooling Calculations
    # CEme = CEelecp + CEcool + CEw + CEeol
    # CEelecp = CE resulting from generation of electricity for pumping of emulsion
    # CEcool = CE from manufacturing undiluted metalworking fluid coolant
    # CEw = CE from processing mains water for coolant
    # CEeol = CE from disposal of mixed emulsion coolant at end of life
    ##########################################################################

    #######################
    # CE_elecp calculations
    #######################
    total_pump_elec = elec_pump_power*machhrs_per_yr   # kWh
    st.session_state.CE_elecp = total_pump_elec*CI_elec

    ######################
    # CE_cool calculations
    ######################
    st.session_state.CE_cool = mwf_per_yr*mwf_CEfactor

    ###################
    # CE_w calculations
    ###################
    st.session_state.CE_w = water_per_yr*water_CEfactor

    ####################
    # CEeol calculations
    ####################
    # evaporating emulsion at end of life. 
    # NB these calculations only done as a sense check. 
    # In reality only applying the emulsion_disposal_CEfactor to entire emulsion
    # CE from electrical energy consumption for water disposal
    eol_elec_perlite = (T_final-T_initial)*shcp_water + LH_water   # kJ/litre
    eol_elec_total = eol_elec_perlite*water_per_yr   # kJ
    CE_eol_elec = (eol_elec_total/3600)*CI_elec   #  kg CO2

    # CE for mwf disposal and total
    nsump,remaining = divmod(sumpchanges_per_yr,1)
    if (remaining > 1.e-5):
        nsump = nsump + 1
    CE_eol_emulsion = nsump*sump_vol*emulsion_disposal_CEfactor
    st.session_state.CE_eol = CE_eol_emulsion    # electricity for evaporation not used here

    # Total equivalent emissions
    st.session_state.CE_me = st.session_state.CE_elecp + \
        st.session_state.CE_cool + st.session_state.CE_w + st.session_state.CE_eol
    
    return

# end emulsion_calcs

# Create barchart in matplotlib
def plot_matplotlib_barchart():
    
    fig = plt.figure()
    species = (
        "CE emissions (kg) from emulsion cooling",
    )
    weight_counts = {
        "CE_w": np.array([st.session_state.CE_w,0]),
        "CE_cool": np.array([st.session_state.CE_cool,0]),
        "CE_eol": np.array([st.session_state.CE_eol,0]),
        "CE_elecp": np.array([st.session_state.CE_elecp,0]),
    }
    width = 0.2

    fig, ax = plt.subplots(figsize=(4,5))
    bottom = np.zeros(2)

    for boolean, weight_count in weight_counts.items():
        p = ax.bar(species, weight_count, width, label=boolean, bottom=bottom)
        bottom += weight_count

    ax.set_title("CE emissions (kg) from emulsion cooling")
    ax.legend(loc="center")
    ax.set_ylabel('CE emissions (jg)')

    return plt
    
# end plot_matplotlib_barchart

# Create barchart in plotly
def plot_plotly_barchart():

    # Need to create a pandas dataframce for use within plotly
    CE_w = st.session_state.CE_w
    CE_cool = st.session_state.CE_cool
    CE_eol = st.session_state.CE_eol
    CE_elecp = st.session_state.CE_elecp
    dfCE = pd.DataFrame({'Emulsion cooling': [""], 'CE_w': CE_w, 'CE_cool': CE_cool, 'CE_eol': CE_eol, 'CE_elecp': CE_elecp})

    fig = px.bar(dfCE, x='Emulsion cooling', y=["CE_w", "CE_cool", "CE_eol", "CE_elecp"],
                 labels={
                     "Emulsion cooling": "Emulsion cooling",
                     "y": "CEeq (kg)"},
                 title='CEeq (kg): emissions from emulsion cooling')
    fig.update_yaxes(title='CEeq (kg)')
    st.plotly_chart(fig)

# end plot_plotly_barchart

# Main program
st.title("Emulsion Cooling CO2 Modelling Program")
st.write("This application enables you to calculate the CO2 eq kg cost of emulsion cooling")
st.write("Click the 'CO2 bar chart' tab to display CO2 eq kg bar chart")
st.markdown("---")

# Main program
probdata = set_params()
emulsion_calcs()

tab1, tab2 = st.tabs(["CO2eq (kg) calculator", "CO2eq (kg) bar chart"])

# CO2 eq kg calculator tab
with tab1:
    
    # Create the input slides - Row 1
    row1 = st.columns([1,1,1])

    #  water CE factor
    default_value = 0.153
    st.session_state.water_CEfactor = default_value
    water_CEfactor = row1[0].number_input("Water CE factor (g/litre)", 0.1, 0.2, default_value)
    st.session_state.water_CEfactor = 0.001*water_CEfactor

    #  MWF CE factor
    default_value = 1.2
    st.session_state.mwf_CEfactor = default_value
    mwf_CEfactor = row1[1].number_input("MWF CE factor (kg/litre)", 1.0, 2.0, default_value)
    st.session_state.mwf_CEfactor = mwf_CEfactor

    #  Emulsion disposal CE factor (kg/litre)
    default_value = 0.2
    st.session_state.emulsion_disposal_CEfactor = default_value
    emulsion_disposal_CEfactor = row1[2].number_input("Emulsion disposal CE factor (kg/litre)", 0.1, 0.3, default_value)
    st.session_state.emulsion_disposal_CEfactor = emulsion_disposal_CEfactor


    # Create the input slides - Row 2
    row2 = st.columns([1,1,1])

    #  CI elec (kg/kWh)
    default_value = 0.149
    st.session_state.CI_elec = default_value
    CI_elec = row2[0].number_input("CI elec (kg/kWh)", 0.1, 0.2, default_value)
    st.session_state.CI_elec = CI_elec

    #  Machining hours per year
    default_value = 2000.0
    st.session_state.machhrs_per_yr = default_value
    machhrs_per_yr = row2[1].number_input("Machining hours per year", 1800.0, 2200.0, default_value)
    st.session_state.machhrs_per_yr = machhrs_per_yr

    #  Electrical pumping power (kW)
    default_value = 30.0
    st.session_state.elec_pump_power = default_value
    elec_pump_power = row2[2].number_input("Electrical pumping power (kW)", 0.1, 50.00, default_value)
    st.session_state.elec_pump_power = elec_pump_power

    # Create the input slides - Row 3
    row3 = st.columns([1,1,1])

    #  Water per year (litres)
    default_value = 10560.0
    st.session_state.water_per_yr = default_value
    water_per_yr = row3[0].number_input("Water per year (litres)", 10.0, 15000.00, default_value)
    st.session_state.water_per_yr = water_per_yr
    
    #  MWF per year (litres)
    default_value = 1080.0
    st.session_state.mwf_per_yr = default_value
    mwf_per_yr = row3[1].number_input("MWF per year (litres)", 1.0, 2000.00, default_value)
    st.session_state.mwf_per_yr = mwf_per_yr
 
    #  Sump changes per year
    default_value = 4.0
    st.session_state.sumpchanges_per_yr = default_value
    sumpchanges_per_yr = row3[2].number_input("Sump changes per year", 0.4, 5.0, default_value)
    st.session_state.sumpchanges_per_yr = sumpchanges_per_yr

    # Create the input slides - Row 4
    row4 = st.columns([1,1,1])
    
    #  Sump volume (litres)
    default_value = 3000.0
    st.session_state.sump_vol = default_value
    sump_vol = row4[0].number_input("Sump volume (litres)", 10.0, 5000.0, default_value)
    st.session_state.sump_vol = sump_vol

    emulsion_calcs()
    st.write("Emulsion CO2eq (kg)",st.session_state.CE_me)

# Cost bar chart tab
with tab2:
    plot_plotly_barchart()





