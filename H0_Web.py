#Libraries

from time import time
from PIL import Image
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import streamlit as st
from astropy import constants as const
from H0live import *
if 'image' not in st.session_state:
    st.session_state.image = None


###########################################
title= 'Latest Standard Siren Measurement'
st.set_page_config(page_title=r'$H_Website$', 
                               initial_sidebar_state= 'expanded',layout="centered")
sb = st.sidebar



#add LOGO.
c1, c2 = st.columns([3, 6])

c1.image('https://yt3.ggpht.com/dsz-32urUxdYKd8a6A2cnmOAo7zCXBtKFXGm_eRjRdYFkqc3IWnKhpAkjY62ATQCLVqLyH7POQ=s900-c-k-c0x00ffffff-no-rj')

st.title(title)

def list_events(csv_file):
    ev1=pd.read_csv(csv_file,sep=",",engine='python')
    return ev1.columns[1:].values.tolist()


evl_list = list_events('test.csv')
#Menu. Separate events from counterparties
ev1_list=list_events('test.csv')

LLo=[]
for i in range(len(ev1_list)):
    if ev1_list[i][0:8] not in LLo:
        LLo.append(ev1_list[i][0:8])
ctp=[]
for i in range(len(ev1_list)):
    if ev1_list[i][9:12] not in ctp:
        ctp.append(ev1_list[i][9:12])
LLok=[]

sb.header("Events")
for i in range(len(LLo)):
    default_value=LLo[0]
    LLok.append(st.sidebar.checkbox(LLo[i],value=default_value))
    

stb_list=[]


for i in range(len(LLok)):
    ctp_list=[]
    for x in range(len(ctp)):
        if LLo[i]+"_"+ctp[x] in ev1_list:
            ctp_list.append(ctp[x])
    stb_list.append(st.selectbox("Counterpart "+str(i+1),ctp_list,key=str(i+1),label_visibility="collapsed"))

#To select the desired prior
prior_list=['uniform', 'log']
choice = st.selectbox("Priors",prior_list) 


#H0live action
choice_list1=[]
for i in range(len(LLok)):
    if LLok[i]==True:
        choice_list1.append(LLo[i]+"_"+stb_list[i])



def plotLL(choice_list1):
    if choice== 'uniform' or 'log':
        h0c= H0live(choice_list1, choice)
        #image = Image.open('H0_combined_posterior.png')
        #st.session_state.image = image



#if st.session_state.image is not None:
 #   st.image(st.session_state.image)   

if st.button('Calculate'):
    plotLL(choice_list1)

#For the graph 

#if st.session_state.image is True:
 #   st.image(st.session_state.image)

if 'image'  in st.session_state:
    st.session_state.image = True
with open('H0_combined_posterior.png', "rb") as file:
    btn = st.download_button(
    label="Download image",
    data=file,
    file_name="'H0_combined_posterior.png'",
    mime="image/png"
    )       

if 'image'  in st.session_state:
    st.session_state.image = False
# Sidebar
sb.header("Related information")
sb.markdown("About gravitational wave events: [GraceDB](https://gracedb.ligo.org/api/events/)")
sb.markdown(
    "What is LIGO?: [LIGO](https://www.ligo.org/about.php)")

sb.markdown(
    "How can GW be used to estimate H0? : [Measuring the Expansion of the Universe with Gravitational Waves](https://www.ligo.org/science/Publication-GW170817Hubble/)")
