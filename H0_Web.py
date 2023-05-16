"""
Script for website 

Luis Miguel Galvis E
"""

#Libraries
import streamlit as st
from PIL import Image
from H0live import *
from numpy import where,array
import json

###########################################
#Session status
if 'object' not in st.session_state:
    st.session_state.object = None


sb = st.sidebar

st.title('$H_0$ GW estimator')

#add columns for subtitle and LOGO.
col1, col2 = st.columns([7, 2])

with col1:
    st.subheader('An estimator for the Hubble Constant based on gravitational wave and multi-messenger observations')

with col2:
    image = Image.open('LVK_rainbow_dark.png')
    st.image(image)

sb.header("Adjust the assumptions that are used when estimating the Hubble constant")

csvfile='bright_sirens.csv'
jsonfile='bright-sirens.json'

#Function to read the csv file and get the events
def list_events_old(csv_file):
    ev1=pd.read_csv(csv_file,sep=",",engine='python')
    return ev1.columns[1:].values.tolist()

class list_events:
    def __init__(self,jsonfile):
        jsonin=json.load(open(jsonfile))
        self.evlist={}
        for gwev in jsonin:
            gwname=jsonin[gwev]['display_name']
            self.evlist[gwname]={}
            self.evlist[gwname]['counterpart']=[]
            self.evlist[gwname]['column']=[]
            for emev in jsonin[gwev]['Counterparts']:
                emname=jsonin[gwev]['Counterparts'][emev]['display_name']
                self.evlist[gwname]['counterpart'].append(emname)
                self.evlist[gwname]['column'].append(jsonin[gwev]['Counterparts'][emev]['column_name'])
        return
    
    def list(self):
        return self.evlist
    def getcolumn(self,gwev,emev):
        print(gwev,emev,self.evlist[gwev]['counterpart'])
        print(np.argwhere(self.evlist[gwev]['counterpart']==emev))
        return self.evlist[gwev]['column'][np.where(np.array(self.evlist[gwev]['counterpart'])==emev)[0][0]]

ev_list = list_events(jsonfile)
dictionary=ev_list.list()
print(dictionary)

#To create the lists to be used
Events=[]
Events_in_checbox=[]
Counterpart_in_selectbox=[]

#To create the sidebar form
with sb.form("My form"):
#To select the events and their counterparts
    st.subheader("Events and counterparts")
    st.markdown("""Select the GW events you want to include, and its EM counterpart:""")
    for key in dictionary:
        if Events_in_checbox==[] and Counterpart_in_selectbox==[]:
            Events_in_checbox.append(st.checkbox(key,True))
            Events.append(key)
            Counterpart_in_selectbox.append(st.selectbox("Counterpart ",dictionary[key]['counterpart'],key=key,label_visibility="collapsed"))
        else:
            Events_in_checbox.append(st.checkbox(key))
            Events.append(key)
            Counterpart_in_selectbox.append(st.selectbox("Counterpart ",dictionary[key]['counterpart'],key=key,label_visibility="collapsed"))
    
 
#To select the desired prior
    #st.markdown("""Select the prior you want to use for the $H_0$ estimation:""")
    prior_list=['uniform', 'log']
    choice = st.selectbox("**Prior**",prior_list) 

#To select additional H0 estimates and the plot of Individual event likelihoods 
    st.subheader("Additional values")
    add_values=['Planck H0 estimate', 'SHOES H0 estimate', 'Individual event likelihoods']
    add_values_choice=[]
    for i in range(len(add_values)):
        add_values_choice.append(st.checkbox(add_values[i])) 



#To create the list of events and their counterparts chosen
    choice_list1=[]
    for i in range(len(Events_in_checbox)):
        if Events_in_checbox[i]==True:
            choice_list1.append(ev_list.getcolumn(Events[i],str(Counterpart_in_selectbox[i])))
            # choice_list1.append(str(Events[i])+"_"+str(Counterpart_in_selectbox[i]))


     
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
        # choice_list2.append(str(Events[0])+"_"+str(dictionary[Events[0]][0]))
        choice_list2.append(ev_list.getcolumn(Events[0],str(Counterpart_in_selectbox[0])))
        h0live_output=H0live(choice_list2, choice,planck=add_values_choice[0],riess=add_values_choice[1],likelihood_plot=add_values_choice[2],data_download=True,likelihood_fname=csvfile)
        csv = h0live_output.H0data_download.to_csv(index=False)
                
        sb.download_button(
        "Download data",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv')  
#If events are selected
    if Calculated:
        st.session_state.object=H0live(choice_list1, choice,planck=add_values_choice[0],riess=add_values_choice[1],likelihood_plot=add_values_choice[2],data_download=True,likelihood_fname=csvfile)
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
            h0live_output=H0live(choice_list1, choice,planck=add_values_choice[0],riess=add_values_choice[1],likelihood_plot=add_values_choice[2],data_download=True,likelihood_fname=csvfile)
            csv = h0live_output.H0data_download.to_csv(index=False)
            b=sb.download_button(
            "Download csv file",
            csv,
            "file.csv",
            "text/csv",
            key='download-csv')  

# To add the information about the website
#sb.header("Related information")
#sb.subheader("What is $H_0$?")
#sb.markdown(r"""$H_0$ is a cosmological parameter which measure 
#            the speed of the expansion of the Universe""")

#sb.subheader("How can we  estimate $H_0$ with bright sirens?")
#sb.markdown(r"""
#Bright sirens are astrophysical systems producing detectable electromagnetic (EM) and gravitational waves (GW), allowing to estimate their redshift, using EM observations, and distance, using GW observations.
#At low redshift H_0 is approximately the inverse of slope of the distance-redshift relation, also known as the Hubble diagram.
#               """)

#sb.markdown(
#    "What are [LIGO](https://www.ligo.org/about.php), [Virgo](https://www.virgo-gw.eu/) and [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/)?")

#sb.markdown(
#    "How can GW be used to estimate H0? : [Measuring the Expansion of the Universe with Gravitational Waves](https://www.ligo.org/science/Publication-GW170817Hubble/)")

st.subheader('How fast is the Universe expanding?')
st.markdown("""
            Astronomers measure this with the “Hubble constant”, measured by comparing the apparent 
            velocity of objects with their distance as the space between them and us stretches. 
            These can be hard to measure, so astronomers normally estimate the likelihood that any 
            given value is correct. 
            The plot above shows the estimate of how likely a given value of the Hubble Constant (often 
            called $H_0$) is based on gravitational wave (GW) and their counterparts detected using 
            electromagnetic (EM) waves. Use the sidebar on the left to select which events, and which 
            counterparts, you want to include in your estimate and update the plot. 
            """)

st.divider()
st.subheader('How results are constructed?')
st.markdown("""
            Gravitational Wave observations LIGO, Virgo and KAGRA allow astronomers make an estimate of 
            the distance to any particular event. With multiple detectors (preferably three or more) it’s 
            also possible to identify roughly where on the sky the event is. Other astronomers, using 
            telescopes sensitive to electromagnetic waves with wavelengths from radio to gamma rays, 
            including optical light, can look for any new sources of light in the sky at that location. 
            If they find a new source which matches the time and location of the gravitational wave source,
            and can pinpoint the exact galaxy, then it’s possible to determine how fast that galaxy appears 
            to be moving away due to the expansion of the Universe. 

            By dividing the apparent velocity (in km/s) by the distance to the source (in Megaparsecs, or 
            Mpc, where 1 Mpc is just over 3 million light years) we can calculate the expansion rate. First 
            publicised by Edwin Hubble, this is called the Hubble constant, and is measured in units of 
            “km/s per Mpc” and a typical value is around 70 km/s/Mpc - i.e. for every Mpc of distance from 
            us, a galaxy’s apparent velocity increases by around 70 km/s.

            Other techniques, using supernova explosions (the SH0ES survey) and measurements of the very 
            early Universe (the Planck satellite), currently disagree with each other, with values of 
            around 73 km/s/Mpc and 67 km/s/Mpc respectively (which you can add to the plot if you like). 
            Gravitational waves, by making an independent measurement of the distance, might be able to 
            shed light on this apparent discrepancy.

            The challenge is, existing gravitational wave detectors don’t measure the distance very 
            precisely - only to around a factor of two - and we may not identify exactly which galaxy it 
            originated from. That means that we can use knowledge of the statistics of the measurements to 
            calculate how likely it is that a given value of the Hubble constant based on the gravitational 
            wave and electromagnetic wave measurements. 

            The likelihoods also depend on which events, and which counterparts, you decide to include, 
            which you can select in the left sidebar.
            """)

st.divider()
st.subheader('This is only a public, preliminary, scientifically inaccurate result')
st.markdown("""
            The estimates of the Hubble Constant provided here are not intended to be a fully 
            scientifically accurate estimate. That’s because when cosmologists do this properly, 
            they are very careful with what prior assumptions they are making, and exactly how they 
            compute the $H_0$ value. The information here comes from the publicly available data published 
            by the LIGO-Virgo-KAGRA collaboration, as well as publicly available data from EM counterpart 
            measurements. Cosmologists may also include different estimates of the likelihood of whether 
            a particular event corresponds to its counterpart, which this website does not do. There are 
            also sometimes different measurements of the apparent velocities of galaxies, which can change 
            the answer. 

            Anyone wishing to make their own estimate for scientific purposes should use the source data 
            at GraceDB for gravitational waves, and any one of a number of catalogues for electromagnetic 
            observations.
            """)

st.divider()
st.subheader('How to cite this website?')
st.markdown("""
            If you would like to use the plot on this website, then please do so. Please quote the URL, 
            with credit to the LIGO-Virgo-KAGRA Collaboration. Please note that users will not necessarily 
            use the same events that you have selected, and that the options may change over time.
            """)

st.divider()
st.subheader('Additional information')
st.markdown("""
            If you have questions about this, please visit https://ask.igwn.org

            What are [LIGO](https://www.ligo.org/about.php), [Virgo](https://www.virgo-gw.eu/) and [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/)?

            **How can GW be used to estimate H0?:** [Measuring the Expansion of the Universe with Gravitational Waves](https://www.ligo.org/science/Publication-GW170817Hubble/)


            """)

st.divider()
st.subheader('Credits and contacts')
st.markdown("""
            The website is provided on behalf of the LIGO-Virgo-KAGRA collaboration. It was developed by <>. 
            If you find an issue with the website, please report it on the Github repository 
            [H0WEBSITE](https://github.com/SergioVallejoP/H0WEBSITE).
            """)


#st.divider()
#st.subheader("How to use the H0 calculator?")
#st.markdown("""On the left you can choose which gravitational wave event and 
#            corresponding electromagnetic counterpart  to use to estimate H0. 
#            Once you have selected the GW events with the checkbox, for GW events with more than 
#            one EM counterpart, you can choose between the different counterparts using the dropdown 
#            menu.
#            The plot shows the posterior obtained from combining the different 
#            likelihoods corresponding to the GW event EM counterpart combinations you have chosen.""")