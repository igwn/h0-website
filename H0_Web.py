"""
Script for website 

Luis Miguel Galvis E
"""

#Libraries
import streamlit as st
from H0live import *

###########################################
#Session status
if 'object' not in st.session_state:
    st.session_state.object = None

title= 'Latest Standard Siren Measurement'

sb = st.sidebar

#add LOGO.
c1, c2 = st.columns([3, 6])

c1.image('https://yt3.ggpht.com/dsz-32urUxdYKd8a6A2cnmOAo7zCXBtKFXGm_eRjRdYFkqc3IWnKhpAkjY62ATQCLVqLyH7POQ=s900-c-k-c0x00ffffff-no-rj')

st.title(title)

#Function to read the csv file and get the events
def list_events(csv_file):
    ev1=pd.read_csv(csv_file,sep=",",engine='python')
    return ev1.columns[1:].values.tolist()

evl_list = list_events('test.csv')

#Function to create the dictionary with the events and their counterparts
dictionary={}

for i in range(len(evl_list)):
    if evl_list[i].split('_')[0] in dictionary:
        dictionary[evl_list[i].split('_')[0]].append(evl_list[i].split('_')[1])
    else:
        dictionary[evl_list[i].split('_')[0]]=[evl_list[i].split('_')[1]]

#To create the lists to be used
Events=[]
Events_in_checbox=[]
Counterpart_in_selectbox=[]

#To create the sidebar
with sb.form("My form"):
#To select the events and their counterparts
    st.header("Events and counterparts")
    for key in dictionary:
        if Events_in_checbox==[] and Counterpart_in_selectbox==[]:
            Events_in_checbox.append(st.checkbox(key,True))
            Events.append(key)
            Counterpart_in_selectbox.append(st.selectbox("Counterpart ",dictionary[key],key=key,label_visibility="collapsed"))
        else:
            Events_in_checbox.append(st.checkbox(key))
            Events.append(key)
            Counterpart_in_selectbox.append(st.selectbox("Counterpart ",dictionary[key],key=key,label_visibility="collapsed"))
    
 
#To select the desired priors
    prior_list=['uniform', 'log']
    choice = st.selectbox("Priors",prior_list) 

#To select confidence levels
    st.subheader("Confidence levels")
    c_levels=['Planck', 'SHOES']
    c_levels_choice=[]
    for i in range(len(c_levels)):
        c_levels_choice.append(st.checkbox(c_levels[i])) 

#To select individual likelihood

    st.subheader("Individual likelihoods")
    individual_L_choice=st.checkbox('plot')
    

#To create the list of events and their counterparts chosen
    choice_list1=[]
    for i in range(len(Events_in_checbox)):
        if Events_in_checbox[i]==True:
            choice_list1.append(str(Events[i])+"_"+str(Counterpart_in_selectbox[i]))


     
    #To calculate the H0    
    Calculated = st.form_submit_button("Calculate")   

#When no event is selected
if choice_list1==[]:
    if  Calculated or not Calculated:
        st.write(r"Please select an event and its counterpart.")

    

#Default values starting the program
else:
    choice_list2=[]

    if not Calculated:
        choice_list2.append(str(Events[0])+"_"+str(dictionary[Events[0]][0]))
        h0live_output=H0live(choice_list2, choice,planck=c_levels_choice[0],riess=c_levels_choice[1],likelihood_plot=individual_L_choice,data_download=True)
        csv = h0live_output.H0data_download.to_csv(index=False)
                
        sb.download_button(
        "Press to Download",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv')  
#If events are selected
    if Calculated:
        st.session_state.object=H0live(choice_list1, choice,planck=c_levels_choice[0],riess=c_levels_choice[1],likelihood_plot=individual_L_choice,data_download=True)
        csv = st.session_state.object.H0data_download.to_csv(index=False)
        a=sb.download_button(
        "Download csv file",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv')     
        
#To work outside of form without disappearing the image
    if not Calculated:
        if st.session_state.object is not None:
            h0live_output=H0live(choice_list1, choice,planck=c_levels_choice[0],riess=c_levels_choice[1],likelihood_plot=individual_L_choice,data_download=True)
            csv = h0live_output.H0data_download.to_csv(index=False)
            b=sb.download_button(
            "Download csv file",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv')  

# To add the information about the website
sb.header("Related information")
sb.subheader("What is $H_0$?")
sb.markdown(r"""$H_0$ is a cosmological parameter which measure 
            the speed of the expansion of the Universe""")

sb.subheader("How can we  estimate $H_0$ with bright sirens?")
sb.markdown(r"""
Bright sirens are astrophysical systems producing detectable electromagnetic (EM) and gravitational waves (GW), allowing to estimate their redshift, using EM observations, and distance, using GW observations.
At low redshift H_0 is approximately the inverse of slope of the distance-redshift relation, also known as the Hubble diagram.

                """)

sb.markdown(
    "What are [LIGO](https://www.ligo.org/about.php), [Virgo](https://www.virgo-gw.eu/) and [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/)?")

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



   
