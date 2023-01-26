#Libraries

from time import time
from PIL import Image
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import streamlit as st
from astropy import constants as const
from bokeh.plotting import figure
from H0live import *

###########################################
title= 'Latest Standard Siren Measurement'
st.set_page_config(page_title='$H_Website$', 
                               initial_sidebar_state= 'expanded',layout="centered")

if 'image' not in st.session_state:
    st.session_state.image = None

#add LOGO.
c1, c2 = st.columns([3, 6])

c1.image('https://yt3.ggpht.com/dsz-32urUxdYKd8a6A2cnmOAo7zCXBtKFXGm_eRjRdYFkqc3IWnKhpAkjY62ATQCLVqLyH7POQ=s900-c-k-c0x00ffffff-no-rj')

st.title(title)

def list_events(csv_file):
    ev1=pd.read_csv(csv_file,sep=",",engine='python')
    return ev1.columns[1:].values.tolist()
#Menu
ev1_list=list_events('test.csv')


st.header('Events')
LLok=[]
for i in range(len(ev1_list)):
    LLok.append(st.checkbox(ev1_list[i]))


prior_list=['uniform', 'log']
choice = st.selectbox("Priors",prior_list)        

#H0live action
def plotLL(LLok):
    choice_list=[]
    for i in range(len(LLok)):
        if LLok[i]==True:
            choice_list.append(ev1_list[i])

    if choice== 'uniform' or 'log':
        h0c= H0live(choice_list, choice)
        image = Image.open('H0_combined_posterior.png')
        st.session_state.image = image



if st.button('Calculate'):
    plotLL(LLok)

if st.session_state.image is not None:
    st.image(st.session_state.image)

with open('H0_combined_posterior.png', "rb") as file:
    btn = st.download_button(
    label="Download image",
    data=file,
    file_name="'H0_combined_posterior.png'",
    mime="image/png"
    )       


sb = st.sidebar
sb.header("Related information")
sb.markdown("About gravitational wave events: [GraceDB](https://gracedb.ligo.org/)")
sb.markdown(
    "What is LIGO?: [LIGO](https://www.ligo.org/about.php)")

sb.markdown(
    "How can GW be used to estimate H0? : [Measuring the Expansion of the Universe with Gravitational Waves](https://www.ligo.org/science/Publication-GW170817Hubble/)")
