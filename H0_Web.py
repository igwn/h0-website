"""
Script for website 

Luis Miguel Galvis E
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
st.set_page_config(page_title=r"""$H_0$Website""", 
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

#To select confidence levels
sb.subheader("Confidence levels")
c_levels=['planck', 'riess']
c_levels_choice=[]
for i in range(len(c_levels)):
    c_levels_choice.append(st.sidebar.checkbox(c_levels[i])) 
c_levels_choice

#H0live action
choice_list1=[]
for i in range(len(LLok)):
    if LLok[i]==True:
        choice_list1.append(str(LLo[i])+"_"+str(stb_list[i]))


#Plot
def plotLL(choice_list1):
    if choice== 'uniform' or 'log':
        h0c= H0live(choice_list1, choice,planck=c_levels_choice[0],riess=c_levels_choice[1])

#Default if no event is selected
if choice_list1==[]:
    choice_list1.append(str(LLo[0])+"_"+str(stb_list[0]))
    plotLL(choice_list1)

#plotLL(choice_list1)
if sb.button('Calculate')==True:
    plotLL(choice_list1)
    







# Sidebar
sb.header("Related information")
sb.subheader("What is $H_0$?")
sb.markdown(r"""$H_0$ is a cosmological parameter which measure 
             the speed of the expansion of the Universe""")

sb.subheader("How can we  estimate $H_0$ with bright sirens?")
sb.markdown(r"""
Bright sirens are astrophysical systems producing detectable electromagnetic (EM) and gravitational waves (GW), allowing to estimate their redshift, using EM observations, and distance, using GW observations.
At low redshift H_0 is approximately the inverse of slope of the distance-redshift relation, also known as the Hubble diagram.

                 """)
#sb.markdown("About gravitational wave events: [GraceDB](https://gracedb.ligo.org/api/events/)")
sb.markdown(
    "What is LIGO?: [LIGO](https://www.ligo.org/about.php)")

sb.markdown(
    "How can GW be used to estimate H0? : [Measuring the Expansion of the Universe with Gravitational Waves](https://www.ligo.org/science/Publication-GW170817Hubble/)")




st.subheader("How to use the H0 calculator?")
st.markdown("""On the left you can choose which gravitational wave event and 
              corresponding electromagnetic counterpart  to use to estimate H0. 
              Once you have selected the GW events with the checkbox, for GW events with more than 
              one EM counterpart, you can choose between the different counterparts using the dropdown 
              menu.
              The plot shows the posterior obtained from combining the different 
              likelihoods corresponding to the GW event EM counterpart combinations you have chosen.""")
