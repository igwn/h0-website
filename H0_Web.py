"""
Script for website 

Luis Miguel Galvis
"""

#Libraries

from time import time
from PIL import Image
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import streamlit as st
from astropy import constants as const
from H0live import *

###########################################

title= 'Latest Standard Siren Measurement'
st.set_page_config(page_title=r'$H_Website$', 
                               initial_sidebar_state= 'expanded',layout="centered")
sb = st.sidebar

#add LOGO.
c1, c2 = st.columns([3, 6])

c1.image('https://yt3.ggpht.com/dsz-32urUxdYKd8a6A2cnmOAo7zCXBtKFXGm_eRjRdYFkqc3IWnKhpAkjY62ATQCLVqLyH7POQ=s900-c-k-c0x00ffffff-no-rj')

st.title(title)
@st.experimental_memo 
def list_events(csv_file):
    ev1=pd.read_csv(csv_file,sep=",",engine='python')
    return ev1.columns[1:].values.tolist()


evl_list = list_events('test.csv')

dictionary={}
for i in range(len(evl_list)):
    if evl_list[i].split('_')[0] in dictionary:
        dictionary[evl_list[i].split('_')[0]].append(evl_list[i].split('_')[1])
    else:
        dictionary[evl_list[i].split('_')[0]]=[evl_list[i].split('_')[1]]

LLo=[]
LLok=[]
stb_list=[]
sb.header("Events and counterparts")
for key in dictionary:
    LLok.append(st.sidebar.checkbox(key))
    LLo.append(key)
    stb_list.append(st.sidebar.selectbox("Counterpart ",dictionary[key],key=key,label_visibility="collapsed"))
 
#To select the desired prior
prior_list=['uniform', 'log']
choice = st.sidebar.selectbox("Priors",prior_list) 

#H0live action
choice_list1=[]
for i in range(len(LLok)):
    if LLok[i]==True:
        choice_list1.append(str(LLo[i])+"_"+str(stb_list[i]))

#Default if no event is selected
if choice_list1==[]:
    choice_list1.append(str(LLo[0])+"_"+str(stb_list[0]))

#Plot
def plotLL(choice_list1):
    if choice== 'uniform' or 'log':
        h0c= H0live(choice_list1, choice)
           
plotLL(choice_list1)

# Sidebar
sb.header("Related information")
sb.markdown("About gravitational wave events: [GraceDB](https://gracedb.ligo.org/api/events/)")
sb.markdown(
    "What is LIGO?: [LIGO](https://www.ligo.org/about.php)")

sb.markdown(
    "How can GW be used to estimate H0? : [Measuring the Expansion of the Universe with Gravitational Waves](https://www.ligo.org/science/Publication-GW170817Hubble/)")


st.subheader("User instructions")

st.markdown("""Through this web page you will be able to estimate live the posterior combined 
            H0 from the pre-calculated likelihood. In the left side bar you will be able to 
            choose the different gravitational wave events and their respective electromagnetic 
            counterparts (EM). You can view results for individual events or combine them""")

st.subheader("Version summary:")
st.markdown("""

* altair 4.2.0
* astropy 5.1.1
* bokeh 2.4.3
* gwosc 0.6.1
* gwpy 3.0.0
* healpy 1.16.1
* ligo_segments 1.4.0
* matplotlib 3.5.2
* numpy 1.21.5
* pandas 1.4.3
* Pillow 9.3.0
* plotly 5.11.0
* requests 2.25.1
* scipy 1.8.1
* streamlit 1.14.1
* ligo.skymap 1.0.3


""")
