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
                               initial_sidebar_state='collapsed',layout="centered")


#add LOGO
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


def plotLL(LLok):
    choice_list=[]
    for i in range(len(LLok)):
        if LLok[i]==True:
            choice_list.append(ev1_list[i])
            
    if choice== 'uniform' or 'log':
        h0c= H0live(choice_list, choice)
        image = Image.open('H0_combined_posterior.png')
        st.image(image)  
        with open('H0_combined_posterior.png', "rb") as file:
            btn = st.download_button(
            label="Download image",
            data=file,
            file_name="'H0_combined_posterior.png'",
            mime="image/png"
            )



if st.button('Calculate'):
    plotLL(LLok)


        




