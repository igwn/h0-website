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
    
page = st.radio('Select Section:', [1,2,3], format_func=headerlabel)

st.markdown("## {}".format(headerlabel(page)))
#Prior section
if page==1:
    c3, c4 = st.columns([3, 7])
    c3.markdown('### Prior 1 ')
    c3.markdown(r'$H_0 max=20$ ')
    c3.markdown(r'$H_0 min=140$ ')
    c3.markdown(r'$\Omega$=0.3')
    c4.markdown('### Prior 2 ')
    c4.markdown(r'$H_0 max=25$ ')
    c4.markdown(r'$H_0 min=135$ ')
    c4.markdown(r'$\Omega$=0.35')
 


#Info section
if page==2:
   menu=["GW170817_info","GW170817_xxx"]
   choice = st.selectbox("Menu",menu)
   if choice == "GW170817_info":
      image = Image.open('probability_H0_plot.png')

      st.image(image)
      st.markdown("This graph was generated with:")          
      st.markdown("* GW170817.")  
      with open("probability_H0_plot.png", "rb") as file:
          btn = st.download_button(
          label="Download the posterior 2",
          data=file,
          file_name="probability_H0_plot.png",
          mime="image/png"
          )
   if choice == "GW170817_xxx":
      image = Image.open('probability_H0_plot-1.png')

      st.image(image)
      st.markdown("This graph was generated with:")       
      st.markdown("* GW170817xxx.")  
      with open("probability_H0_plot.png", "rb") as file:
          btn = st.download_button(
          label="Download the posterior 3",
          data=file,
          file_name="probability_H0_plot-1.png",
          mime="image/png"
          )

#Interactive section
if page==3:

     menu= ["GW170817_info and prior 1","GW170817_info and prior 2","GW170817_xxx and prior 1","GW170817_xxx and prior 2", "GW170817_info and GW170817xxx and prior 1"]
     choice = st.selectbox("Menu",menu)
  

     if choice == "GW170817_info and prior 1":
         image = Image.open('probability_H0_plot.png')

         st.image(image)
         st.markdown("This graph was generated with:")          
         st.markdown("* GW170817.")  
         st.markdown("* Prior 1.")  
         with open("probability_H0_plot.png", "rb") as file:
             btn = st.download_button(
             label="Download the posterior 4",
             data=file,
             file_name="probability_H0_plot.png",
             mime="image/png"
            )

     if choice == "GW170817_info and prior 2":
         image = Image.open('probability_H0_plot_1.png')

         st.image(image)
         st.markdown("This graph was generated with:")          
         st.markdown("* GW170817.")  
         st.markdown("* Prior 2.")  
         with open("probability_H0_plot_1.png", "rb") as file:
             btn = st.download_button(
             label="Download the posterior 5",
             data=file,
             file_name="probability_H0_plot_1.png",
             mime="image/png"
            )
     if choice == "GW170817_xxx and prior 1":
            image = Image.open('probability_H0_plot-1.png')

            st.image(image)
            st.markdown("This graph was generated with:")       
            st.markdown("* GW170817xxx.") 
            st.markdown("* Prior 1")  
            with open("probability_H0_plot-1.png", "rb") as file:
                btn = st.download_button(
                label="Download the posterior 6",
                data=file,
                file_name="probability_H0_plot-1.png",
                mime="image/png"
                )

     if choice == "GW170817_xxx and prior 2":
            image = Image.open('probability_H0_plot-1_1.png')

            st.image(image)
            st.markdown("This graph was generated with:")       
            st.markdown("* GW170817xxx.") 
            st.markdown("* Prior 2")  
            with open("probability_H0_plot-1_1.png", "rb") as file:
                btn = st.download_button(
                label="Download image option 6",
                data=file,
                file_name="probability_H0_plot-1_1.png",
                mime="image/png"
                )

     if choice == "GW170817_info and GW170817xxx and prior 1":
            image = Image.open('probability_H0_plot_yyy.png')

            st.image(image)
            st.markdown("This graph was generated with:")       
            st.markdown("* GW170817_info and GW170817xxx.") 
            st.markdown("* Prior 1")  
            with open("probability_H0_plot_yyy.png", "rb") as file:
                btn = st.download_button(
                label="Download image option 6",
                data=file,
                file_name="probability_H0_plot_yyy.png",
                mime="image/png"
                )

