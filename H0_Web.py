#Libraries

from time import time
from PIL import Image
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import streamlit as st
from astropy import constants as const
from bokeh.plotting import figure
from H0calculate import *
###########################################
title= 'Latest Standard Siren Measurement'
st.set_page_config(page_title='$H_Website$', 
                               initial_sidebar_state='collapsed',layout="centered")


#add LOGO
c1, c2 = st.columns([3, 6])

c1.image('https://yt3.ggpht.com/dsz-32urUxdYKd8a6A2cnmOAo7zCXBtKFXGm_eRjRdYFkqc3IWnKhpAkjY62ATQCLVqLyH7POQ=s900-c-k-c0x00ffffff-no-rj')

st.title(title)

LNAME=['GW170817_EM1_140_20','GW170817_EM2_140_20','GW291122_EM1_140_20','GW291122_EM2_140_20']
LL=[]
for i in range(len(LNAME)):
    LL.append(pd.read_csv(LNAME[i]+'.csv',sep=",",engine='python'))
#Reading csv file 
#L1=pd.read_csv('H0_prob_H0_GW170817_EM1_140_20.csv',sep=",",engine='python')
#L2=pd.read_csv('H0_prob_H0_GW170817_EM2_140_20.csv',sep=",",engine='python')
#L3=pd.read_csv('H0_prob_H0_GW291122_EM1_140_20.csv',sep=",",engine='python')
#L4=pd.read_csv('H0_prob_H0_GW291122_EM2_140_20.csv',sep=",",engine='python')
LLok=[]
for i in range(len(LNAME)):
    LLok.append(st.checkbox(LNAME[i]))


#LL=[L1,L2,L3,L4]

def plotLL(LLok):
    post=1
    for i in range(len(LL)):
        if LLok[i]==True:
            LLI=np.array(LL[i].iloc[:,2])
            #print(LLI)
            post=post*LLI
    post/=simpson(post,LL[1].iloc[:,1])
    plt.plot (LL[1].iloc[:,1],post)
    plt.xlabel (r'$H_{0}$', size=15)
    plt.ylabel (r'$p(H_{0})$', size=15)
    plt.tight_layout ()
    p = figure(
    title= "Available likelihoods",
    x_axis_label=r'$$H_0$$',
    y_axis_label=r'$$\rho(H_0)$$',width=400, height=400)
    p.line(LL[1].iloc[:,1],post , legend_label='Trend', line_width=2)
    st.bokeh_chart(p, use_container_width=True)


if st.button('Calculate'):
    plotLL(LLok)


        





