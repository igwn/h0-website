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
title= 'Latest Standard Siren Meassurement'
st.set_page_config(page_title='$H_Website$', 
                               initial_sidebar_state='collapsed',layout="centered")


#LOGO in the slide
def add_logo(logo_path, width, height):
    """Read and return a resized logo"""
    logo = Image.open(logo_path)
    modified_logo = logo.resize((width, height))
    return modified_logo

my_logo = add_logo(logo_path="LVK.jpg", width=290, height=200)
st.sidebar.image(my_logo)



#add LOGO
c1, c2 = st.columns([3, 6])

c1.image('https://yt3.ggpht.com/dsz-32urUxdYKd8a6A2cnmOAo7zCXBtKFXGm_eRjRdYFkqc3IWnKhpAkjY62ATQCLVqLyH7POQ=s900-c-k-c0x00ffffff-no-rj')

st.title(title)
image = Image.open('probability_H0_plot.png')

st.image(image,caption="GW170817 measurement of H0")

with open("probability_H0_plot.png", "rb") as file:
    btn = st.download_button(
            label="Download the posterior 1",
            data=file,
            file_name="probability_H0_plot.png",
            mime="image/png"
        )
          

st.markdown("The prior is a flat prior.")






sectionnames = [
                'Priors',
                'Event info and H_0 likelihood',
                'Interactive page for events by choice',
]

def headerlabel(number):
    return "{0}: {1}".format(number, sectionnames[number-1])
st.header('PRIORS')
c3, c4 = st.columns([3, 7])
c3.markdown('### Prior 1 ')
c3.markdown(r'$H_0 max=20$ ')
c3.markdown(r'$H_0 min=140$ ')
c3.markdown(r'$\Omega$=0.3')
c4.markdown('### Prior 2 ')
c4.markdown(r'$H_0 max=25$ ')
c4.markdown(r'$H_0 min=135$ ')
c4.markdown(r'$\Omega$=0.35')
    
#page = st.radio('Select Section:', [1,2,3], format_func=headerlabel)

#st.markdown("## {}".format(headerlabel(page)))
#Prior section

c3, c4 = st.columns([3, 7])
c3.markdown('### Prior 1 ')
c3.markdown(r'$H_0 max=20$ ')
c3.markdown(r'$H_0 min=140$ ')
c3.markdown(r'$\Omega$=0.3')
c4.markdown('### Prior 2 ')
c4.markdown(r'$H_0 max=25$ ')
c4.markdown(r'$H_0 min=135$ ')
c4.markdown(r'$\Omega$=0.35')

#Reading csv file 
H0likelihood_GW170817_EM1_140_20=pd.read_csv('H0_prob_H0_GW170817_EM1_140_20.csv',sep=",",engine='python')
H0likelihood_GW170817_EM2_140_20=pd.read_csv('H0_prob_H0_GW170817_EM2_140_20.csv',sep=",",engine='python')
H0likelihood_GW291122_EM1_140_20=pd.read_csv('H0_prob_H0_GW291122_EM1_140_20.csv',sep=",",engine='python')
H0likelihood_GW291122_EM2_140_20=pd.read_csv('H0_prob_H0_GW291122_EM2_140_20.csv',sep=",",engine='python')

likelihood_array_GW170817_EM1_140_20=np.array(H0likelihood_GW170817_EM1_140_20["GW170817"])
likelihood_array_GW170817_EM2_140_20=np.array(H0likelihood_GW170817_EM2_140_20["GW170817"])
likelihood_array_GW291122_EM1_140_20=np.array(H0likelihood_GW291122_EM1_140_20["GW170817"])
likelihood_array_GW291122_EM2_140_20=np.array(H0likelihood_GW291122_EM2_140_20["GW170817"])

H0_array_GW170817_EM1_140_20=np.array(H0likelihood_GW170817_EM1_140_20["H0_array"])
H0_array_GW170817_EM2_140_20=np.array(H0likelihood_GW170817_EM2_140_20["H0_array"])
H0_array_GW291122_EM1_140_20=np.array(H0likelihood_GW291122_EM1_140_20["H0_array"])
H0_array_GW291122_EM2_140_20=np.array(H0likelihood_GW291122_EM2_140_20["H0_array"])
#Combined
L11=likelihood_array_GW170817_EM1_140_20*likelihood_array_GW170817_EM1_140_20
L12=likelihood_array_GW170817_EM1_140_20*likelihood_array_GW170817_EM2_140_20
L21=likelihood_array_GW170817_EM2_140_20*likelihood_array_GW170817_EM1_140_20
L22=likelihood_array_GW170817_EM2_140_20*likelihood_array_GW170817_EM2_140_20
#Normalization
L11 /= simpson (L11,H0_array_GW170817_EM1_140_20)
L12 /= simpson (L12,H0_array_GW170817_EM1_140_20)
L21 /= simpson (L21,H0_array_GW170817_EM1_140_20)
L22 /= simpson (L22,H0_array_GW170817_EM1_140_20)
menu= ["GW170817_EM1 and GW291122_EM1","GW170817_EM1 and GW291122_EM2","GW170817_EM2 and GW291122_EM1","GW170817_EM2 and GW291122_EM2"]
choice = st.selectbox("Menu",menu)
  
if choice == "GW170817_EM1 and GW291122_EM1":
    plt.plot ( H0_array_GW170817_EM1_140_20, L11)

    plt.xlim (H0_array_GW170817_EM1_140_20 [0], H0_array_GW170817_EM1_140_20 [-1])

    plt.xlabel (r'$H_{0}$', size=15)
    plt.ylabel (r'$p(H_{0})$', size=15)

    plt.tight_layout ()
    p = figure(
    title= r"$$ Meassurement of H_0$$",
    x_axis_label=r'$$H_0$$',
    y_axis_label=r'$$\rho(H_0)$$',width=400, height=400)

    p.line(H0_array_GW170817_EM1_140_20, L11, legend_label='Trend', line_width=2)

    st.bokeh_chart(p, use_container_width=True)

if choice == "GW170817_EM1 and GW291122_EM2":
    plt.plot ( H0_array_GW170817_EM1_140_20, L12)

    plt.xlim (H0_array_GW170817_EM1_140_20 [0], H0_array_GW170817_EM1_140_20 [-1])

    plt.xlabel (r'$H_{0}$', size=15)
    plt.ylabel (r'$p(H_{0})$', size=15)

    plt.tight_layout ()
    p = figure(
    title= r"$$ Meassurement of H_0$$",
    x_axis_label=r'$$H_0$$',
    y_axis_label=r'$$\rho(H_0)$$',width=400, height=400)

    p.line(H0_array_GW170817_EM1_140_20, L12, legend_label='Trend', line_width=2)

    st.bokeh_chart(p, use_container_width=True)

if choice == "GW170817_EM2 and GW291122_EM1":
    plt.plot ( H0_array_GW170817_EM1_140_20, L21)

    plt.xlim (H0_array_GW170817_EM1_140_20 [0], H0_array_GW170817_EM1_140_20 [-1])

    plt.xlabel (r'$H_{0}$', size=15)
    plt.ylabel (r'$p(H_{0})$', size=15)

    plt.tight_layout ()
    p = figure(
    title= r"$$ Meassurement of H_0$$",
    x_axis_label=r'$$H_0$$',
    y_axis_label=r'$$\rho(H_0)$$',width=400, height=400)

    p.line(H0_array_GW170817_EM1_140_20, L21, legend_label='Trend', line_width=2)

    st.bokeh_chart(p, use_container_width=True)

if choice == "GW170817_EM2 and GW291122_EM2":
    plt.plot ( H0_array_GW170817_EM1_140_20, L22)

    plt.xlim (H0_array_GW170817_EM1_140_20 [0], H0_array_GW170817_EM1_140_20 [-1])

    plt.xlabel (r'$H_{0}$', size=15)
    plt.ylabel (r'$p(H_{0})$', size=15)

    plt.tight_layout ()
    p = figure(
    title= r"$$ Meassurement of H_0$$",
    x_axis_label=r'$$H_0$$',
    y_axis_label=r'$$\rho(H_0)$$',width=400, height=400)

    p.line(H0_array_GW170817_EM1_140_20, L12, legend_label='Trend', line_width=2)

    st.bokeh_chart(p, use_container_width=True)

