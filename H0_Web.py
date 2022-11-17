from time import time
from PIL import Image

import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import streamlit as st
from astropy import constants as const
from bokeh.plotting import figure

from H0calculate import *

title= '$H_0$ Website'

st.set_page_config(page_title=title, 
                               initial_sidebar_state='collapsed')

from PIL import Image

# You can always call this function where ever you want

def add_logo(logo_path, width, height):
    """Read and return a resized logo"""
    logo = Image.open(logo_path)
    modified_logo = logo.resize((width, height))
    return modified_logo
#El logo aparece en el slide
my_logo = add_logo(logo_path="LVK.jpg", width=290, height=200)
st.sidebar.image(my_logo)



#st.sidebar.image(add_logo(logo_path="https://yt3.ggpht.com/dsz-32urUxdYKd8a6A2cnmOAo7zCXBtKFXGm_eRjRdYFkqc3IWnKhpAkjY62ATQCLVqLyH7POQ=s900-c-k-c0x00ffffff-no-rj", width=50, height=60))
#De esta manera el logo no aparece a la izquierda por completo
c1, c2 = st.columns([3, 7])
# Contenido de la primera columna
c1.image('https://yt3.ggpht.com/dsz-32urUxdYKd8a6A2cnmOAo7zCXBtKFXGm_eRjRdYFkqc3IWnKhpAkjY62ATQCLVqLyH7POQ=s900-c-k-c0x00ffffff-no-rj')

st.title(title)








sectionnames = [
                'Latest Standard Siren Meassurement',
                'Prior',
                'Event info and $H_0$ likelihood',
                'Interactive page for events by choice',
                'Result of customized choice of events',
]

def headerlabel(number):
    return "{0}: {1}".format(number, sectionnames[number-1])
    
page = st.radio('Select Section:', [1,2,3,4,5], format_func=headerlabel)

st.markdown("## {}".format(headerlabel(page)))
if page==1:
 start = time ()




#plt.plot ( H0_array, pH0)

#plt.xlim (H0_array [0], H0_array [-1])

#plt.xlabel (r'$H_{0}$', size=15)
#plt.ylabel (r'$p(H_{0})$', size=15)

#plt.tight_layout ()

#plt.savefig ('pH0_GW170817_test')

#print ('Time:', time()-start, 'sec')

print ('Time:', time()-start, 'sec')

image = Image.open('probability_H0_plot.png')

st.image(image, caption='Sunrise by the mountains')

#st.bokeh_chart(probability_H0_plot,png, use_container_width=True)